#!/usr/bin/env python3
"""SWTCG Card Cost Analyzer.

Estimates appropriate build costs for new/playtest cards using Ridge regression
against the existing card database. Also generates statistical cost curve reports
and finds comparable existing cards.

Usage:
    python costAnalyzer.py --report [--output FILE]
    python costAnalyzer.py --estimate --type TYPE --power N --health N
                           [--keywords "Accuracy 1, Shields 1"] [--freeform N] [--arenas N]
    python costAnalyzer.py --similar --type TYPE --power N --health N
                           [--keywords "Accuracy 1"] [--cost N | --cost-range MIN MAX] [--n N]
"""

import os
import sys
import re
import json
import argparse
import math
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETS_FOLDER = os.path.join(SCRIPT_DIR, "..", "starwars", "sets")
sys.path.insert(0, SCRIPT_DIR)

from SWTCG import loadAllSets, SETS

IGNORED_FILES = ["HELP.txt", "START.txt"]

# ------------------------------------------------------------------------------
# KEYWORD DEFINITIONS
# ------------------------------------------------------------------------------

# Keywords that take a numeric X value
NUMERIC_KEYWORDS = [
    "Accuracy", "Absorb", "Ambush", "Area Damage", "Avenge", "Backfire",
    "Barrage", "Bombard", "Critical Hit", "Damage Control", "Deflect",
    "Evade", "Focus", "Fury", "Ion Cannon", "Lucky", "Overload", "Parry",
    "Persuade", "Protect", "Resilience", "Retaliate", "Riposte", "Shields",
    "Stun", "Surge", "Tenacity", "Velocity",
]

# Keywords that are boolean (present or absent)
BOOLEAN_KEYWORDS = [
    "Armor", "Consume", "Cunning", "Double Damage", "Double Strike",
    "Ferocity", "Fortitude", "Inspiration", "Intercept", "Intimidation",
    "Meditate", "Overkill", "Precision", "Elude", "Redirect", "Stealth",
]

# Keywords with colon-delimited effects — recognized, counted as 1
COMPOSITE_KEYWORDS = [
    "Adapt", "Alternative Cost", "Bounty", "Deploy", "Enhance", "Equip",
    "Foresight", "Forewarning", "Hidden Cost", "Last Stand",
    "Pilot", "Reduced Cost", "Reserves", "Stack", "Switch", "Upkeep",
]

# Keywords whose value scales with the card's power stat, making a
# power*keyword interaction term mechanically meaningful:
#   Accuracy X:    shifts hit threshold; each extra die adds ~X/6 expected hits
#   Critical Hit X: fires on nat-6; P(trigger) = 1-(5/6)^P -- grows with P
#   Fury X:        fires on nat-4; P(trigger) = 1-(5/6)^P -- also grows with P
POWER_INTERACTION_KEYWORDS = ['Accuracy', 'Critical Hit', 'Fury']

# Matches clauses that grant an effect to ALL of your units/characters/etc.
# These scale with board state and are systematically worth more than
# single-target freeform abilities.
# Covers: "Each of your X gets...", "Each of your other X gets...",
#         "Your other X gets..."
# Excludes: "each of your opponent's X" (effect targets the opponent's board)
ARMY_EFFECT_PATTERN = re.compile(
    r'\beach of your(?!\s+opponent)( other)?\b|\byour other\b',
    re.IGNORECASE
)

# Extracts X from "Pay X Force ->" activation cost prefix.
FORCE_ACTIVATION_PATTERN = re.compile(r'Pay\s+(\d+)\s+Force\s*->', re.IGNORECASE)

# Keyword groups for ceiling + force_cost feature pairs.
# ceiling = sum of values in group; force_cost = total "Pay X Force ->" cost for the group.
PREVENTION_CEILING_KEYWORDS = frozenset({'Absorb', 'Deflect', 'Evade', 'Persuade'})  # self-protection
PROTECT_KEYWORDS            = frozenset({'Protect'})   # ally-protection — separate group
RETALIATE_KEYWORDS          = frozenset({'Retaliate'})
AMBUSH_KEYWORDS             = frozenset({'Ambush'})
_ALL_GROUPED_KEYWORDS = (
    PREVENTION_CEILING_KEYWORDS | PROTECT_KEYWORDS | RETALIATE_KEYWORDS | AMBUSH_KEYWORDS
)


def _build_keyword_patterns():
    """Build regex patterns for keyword extraction. Returns list of (name, pattern, is_numeric)."""
    patterns = []

    # Numeric keywords: "Keyword X" or "Keyword -X" or "Keyword +X"
    # Also handle activated forms: "Pay N Force -> Keyword X" or "[tap] -> Keyword X"
    prefix = r'(?:(?:Pay\s+\d+\s+\w+\s+->|Pay\s+\d+\s+\w+\s+\w+\s+->|\[tap\]\s+->)\s*)?'
    for kw in sorted(NUMERIC_KEYWORDS, key=len, reverse=True):
        pat = re.compile(
            prefix + re.escape(kw) + r'\s+([+-]?\d+(?:\.\d+)?)',
            re.IGNORECASE
        )
        patterns.append((kw, pat, True))

    # Boolean and composite keywords
    for kw in sorted(BOOLEAN_KEYWORDS + COMPOSITE_KEYWORDS, key=len, reverse=True):
        pat = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
        patterns.append((kw, pat, False))

    return patterns


KEYWORD_PATTERNS = _build_keyword_patterns()


def extract_keywords(text):
    """Extract recognized keywords from card text.

    Returns:
        (keywords_dict, freeform_count, army_count,
         prevention_force_cost, protect_force_cost,
         retaliate_force_cost, ambush_force_cost)

        keywords_dict maps keyword name to its numeric value (or 1 for boolean/composite).
        freeform_count is the number of clauses not matched by any keyword.
        army_count is the number of clauses matching "Each of your [other] X" patterns.
        *_force_cost values are the sum of "Pay X Force ->" costs for each keyword group.
    """
    if not text or text in ("[game text]", ""):
        return {}, 0, 0, 0, 0, 0, 0

    # Split on | (pipe is the clause delimiter in SWTCG card text)
    clauses = [c.strip() for c in text.split('|') if c.strip()]

    keywords = {}
    freeform_count = 0
    army_count = 0
    prevention_force_cost = 0
    protect_force_cost = 0
    retaliate_force_cost = 0
    ambush_force_cost = 0

    for clause in clauses:
        matched = False
        matched_kw = None
        for kw_name, pattern, is_numeric in KEYWORD_PATTERNS:
            m = pattern.search(clause)
            if m:
                if is_numeric:
                    val = float(m.group(1))
                    keywords[kw_name] = max(keywords.get(kw_name, 0), val)
                else:
                    keywords[kw_name] = 1
                matched = True
                matched_kw = kw_name
                break  # Each clause counted once

        # For grouped keywords, extract the Force activation cost from this clause.
        if matched_kw in _ALL_GROUPED_KEYWORDS:
            fc_match = FORCE_ACTIVATION_PATTERN.search(clause)
            fc = int(fc_match.group(1)) if fc_match else 0
            if matched_kw in PREVENTION_CEILING_KEYWORDS:
                prevention_force_cost += fc
            elif matched_kw in PROTECT_KEYWORDS:
                protect_force_cost += fc
            elif matched_kw in RETALIATE_KEYWORDS:
                retaliate_force_cost += fc
            elif matched_kw in AMBUSH_KEYWORDS:
                ambush_force_cost += fc

        # Army check is independent of keyword matching: a clause like
        # "Each of your other Jedi gets Foresight..." contains both a
        # keyword and an army-wide grant, and we want to capture both.
        if ARMY_EFFECT_PATTERN.search(clause):
            army_count += 1
        elif not matched:
            freeform_count += 1

    return (keywords, freeform_count, army_count,
            prevention_force_cost, protect_force_cost,
            retaliate_force_cost, ambush_force_cost)


# ------------------------------------------------------------------------------
# CARD LOADING AND PROCESSING
# ------------------------------------------------------------------------------

def get_arenas(typeline):
    """Return list of arenas a card belongs to from its typeline.

    Examples:
        "Space"           -> ["Space"]
        "Space/Ground"    -> ["Space", "Ground"]
        "Ground/Character"-> ["Ground", "Character"]
        "Mission"         -> ["Mission"]
    """
    arenas = []
    for part in typeline.split('/'):
        part = part.strip().lower()
        if part.startswith('space'):
            arenas.append('Space')
        elif part.startswith('ground'):
            arenas.append('Ground')
        elif part.startswith('character'):
            arenas.append('Character')
        elif part.startswith('subordinate'):
            arenas.append('Subordinate')
        elif part.startswith('mission'):
            arenas.append('Mission')
        elif part.startswith('resource'):
            arenas.append('Resource')
        elif part:
            arenas.append(part.title())
    return arenas if arenas else [typeline.strip()]


def load_cards():
    """Load and process all cards from the set database.

    Returns list of processed card dicts with extracted features.
    Excludes Subordinates and cards without a build cost.
    """
    all_cards, _ = loadAllSets(SETS_FOLDER, ignoredFiles=IGNORED_FILES)

    processed = []
    for card in all_cards:
        # Skip cards without a build cost
        cost_str = card.buildCost.strip() if card.buildCost else ""
        if not cost_str or cost_str == "[buildCost]":
            continue

        # Skip subordinates
        if card.rarity == "S":
            continue

        # Parse cost (must be integer)
        try:
            cost = int(cost_str)
        except ValueError:
            continue

        # Parse combat stats (may be absent for non-unit cards)
        def _parse_stat(s):
            if not s or not s.strip():
                return None
            try:
                return int(s.strip())
            except ValueError:
                return None

        power = _parse_stat(card.power)
        health = _parse_stat(card.health)

        # Determine arenas
        arenas = get_arenas(card.typeline)
        unit_arenas = [a for a in arenas if a in ('Space', 'Ground', 'Character')]
        arena_count = len(unit_arenas) if unit_arenas else 1

        # Extract keywords from card text
        (keywords, freeform_count, army_count,
         prevention_force_cost, protect_force_cost,
         retaliate_force_cost, ambush_force_cost) = extract_keywords(card.cardText)

        # Compute group ceilings from the keywords dict
        prevention_ceiling = sum(float(keywords.get(kw, 0)) for kw in PREVENTION_CEILING_KEYWORDS)
        prevention_count   = sum(1 for kw in PREVENTION_CEILING_KEYWORDS if keywords.get(kw, 0) > 0)
        protect_ceiling    = float(keywords.get('Protect', 0))
        retaliate_ceiling  = float(keywords.get('Retaliate', 0))
        ambush_ceiling     = float(keywords.get('Ambush', 0))

        # Flags
        usage = (card.usage or "").strip().upper()
        is_banned = "BANNED" in usage
        is_restricted = "RESTRICTED" in usage

        processed.append({
            'name': card.name,
            'set': card.setCode,
            'cost': cost,
            'power': power,
            'health': health,
            'arenas': arenas,
            'arena_count': arena_count,
            'keywords': keywords,
            'freeform_count': freeform_count,
            'army_count': army_count,
            'prevention_ceiling':    prevention_ceiling,
            'prevention_count':      prevention_count,
            'prevention_force_cost': prevention_force_cost,
            'protect_ceiling':       protect_ceiling,
            'protect_force_cost':    protect_force_cost,
            'retaliate_ceiling':     retaliate_ceiling,
            'retaliate_force_cost':  retaliate_force_cost,
            'ambush_ceiling':        ambush_ceiling,
            'ambush_force_cost':     ambush_force_cost,
            'is_unique': bool(card.uniqueLetter),
            'is_banned': is_banned,
            'is_restricted': is_restricted,
            'rarity': card.rarity,
            'text': card.cardText if card.cardText != "[game text]" else "",
        })

    return processed


def group_by_arena(cards):
    """Group processed cards by arena type.

    Multi-arena cards appear in each of their arena groups.
    """
    by_arena = defaultdict(list)
    for card in cards:
        for arena in card['arenas']:
            by_arena[arena].append(card)
    return by_arena


# ------------------------------------------------------------------------------
# REGRESSION MODEL
# ------------------------------------------------------------------------------

def select_features(cards, min_count=5, min_pct=0.01):
    """Choose keywords to include in regression (appear in enough cards)."""
    kw_counts = defaultdict(int)
    for card in cards:
        for kw in card['keywords']:
            kw_counts[kw] += 1

    threshold = max(min_count, len(cards) * min_pct)
    return [kw for kw, count in sorted(kw_counts.items(), key=lambda x: -x[1])
            if count >= threshold]


def build_feature_matrix(cards, feature_keywords):
    """Build feature matrix and target vector for regression.

    Only uses unit cards (those with valid power and health).

    Features: power, health, per-keyword values, power*keyword interaction
    terms for POWER_INTERACTION_KEYWORDS, freeform_count, army_count, group ceiling and
    force_cost pairs (prevention, protect, retaliate, ambush), is_unique, multi_arena.

    Returns (X, y, feature_names) or (None, None, None) if insufficient data.
    """
    import numpy as np

    unit_cards = [c for c in cards if c['power'] is not None and c['health'] is not None]
    if len(unit_cards) < 10:
        return None, None, None

    # Only add interaction terms for keywords present in this arena's feature set
    interaction_keywords = [kw for kw in POWER_INTERACTION_KEYWORDS if kw in feature_keywords]

    feature_names = (
        ['power', 'health']
        + list(feature_keywords)
        + [f'power*{kw}' for kw in interaction_keywords]
        + ['freeform_count', 'army_count',
           'prevention_ceiling', 'prevention_count', 'prevention_force_cost',
           'protect_ceiling',    'protect_force_cost',
           'retaliate_ceiling',  'retaliate_force_cost',
           'ambush_ceiling',     'ambush_force_cost',
           'is_unique', 'multi_arena']
    )

    rows = []
    y_vals = []
    for card in unit_cards:
        row = [float(card['power']), float(card['health'])]
        for kw in feature_keywords:
            row.append(float(card['keywords'].get(kw, 0)))
        # Interaction terms: power * keyword_value
        for kw in interaction_keywords:
            row.append(float(card['power']) * float(card['keywords'].get(kw, 0)))
        row.append(float(card['freeform_count']))
        row.append(float(card['army_count']))
        row.append(float(card['prevention_ceiling']))
        row.append(float(card['prevention_count']))
        row.append(float(card['prevention_force_cost']))
        row.append(float(card['protect_ceiling']))
        row.append(float(card['protect_force_cost']))
        row.append(float(card['retaliate_ceiling']))
        row.append(float(card['retaliate_force_cost']))
        row.append(float(card['ambush_ceiling']))
        row.append(float(card['ambush_force_cost']))
        row.append(1.0 if card['is_unique'] else 0.0)
        row.append(float(card['arena_count'] - 1))  # 0=single, 1=dual-arena
        rows.append(row)
        y_vals.append(float(card['cost']))

    return np.array(rows), np.array(y_vals), feature_names


def fit_ridge(X, y, alpha=None):
    """Fit Ridge regression with 5-fold CV to select regularization strength.

    Ridge (L2 regularization) differs from OLS in that it adds a penalty
    lambda * sum(beta^2) to the least-squares objective. This:
      - Handles multicollinearity from correlated features (stats, keywords, interactions)
      - Provides more stable estimates for lower-frequency keywords (e.g., Stealth)
      - Introduces slight bias in exchange for reduced variance

    If alpha is None, chooses the best value via 5-fold cross-validation.

    Returns dict with coefficients, R^2, RMSE, selected alpha.
    Note: std_errors are not reported -- Ridge estimates are biased so the
    usual OLS confidence interval formulas don't apply.
    """
    import numpy as np

    n, p = X.shape
    X_aug = np.column_stack([np.ones(n), X])

    # Shuffle data for CV to avoid systematic ordering effects
    rng = np.random.default_rng(42)
    perm = rng.permutation(n)
    X_shuf, y_shuf = X_aug[perm], y[perm]

    if alpha is None:
        # Search over a log-spaced grid of regularization strengths
        alphas = np.logspace(-2, 3, 40)
        best_alpha, best_cv_mse = None, float('inf')
        k = 5
        fold_size = n // k

        for a in alphas:
            # Don't regularize the intercept (first column)
            reg_matrix = np.diag([0.0] + [a] * p)
            mses = []
            for fold in range(k):
                val_start = fold * fold_size
                val_end = val_start + fold_size if fold < k - 1 else n
                val_idx = list(range(val_start, val_end))
                train_idx = list(range(0, val_start)) + list(range(val_end, n))

                X_tr, y_tr = X_shuf[train_idx], y_shuf[train_idx]
                X_val, y_val = X_shuf[val_idx], y_shuf[val_idx]

                try:
                    coeffs = np.linalg.solve(X_tr.T @ X_tr + reg_matrix, X_tr.T @ y_tr)
                    pred = X_val @ coeffs
                    mses.append(float(np.mean((y_val - pred) ** 2)))
                except np.linalg.LinAlgError:
                    mses.append(float('inf'))

            mean_mse = sum(mses) / len(mses)
            if mean_mse < best_cv_mse:
                best_cv_mse = mean_mse
                best_alpha = a

        alpha = best_alpha if best_alpha is not None else 1.0

    # Final fit on all data with the selected alpha
    reg_matrix = np.diag([0.0] + [alpha] * p)
    coeffs = np.linalg.solve(X_aug.T @ X_aug + reg_matrix, X_aug.T @ y)

    y_pred = X_aug @ coeffs
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    rmse = math.sqrt(ss_res / n)

    return {
        'intercept': float(coeffs[0]),
        'coefficients': coeffs[1:].tolist(),
        'std_errors': None,  # Not meaningful for biased Ridge estimates
        'r_squared': r_sq,
        'rmse': rmse,
        'n': n,
        'alpha': float(alpha),
    }


def build_model(cards):
    """Build Ridge regression model for a set of cards.

    Returns model dict or None if insufficient data.
    """
    feature_keywords = select_features(cards)
    X, y, feature_names = build_feature_matrix(cards, feature_keywords)
    if X is None:
        return None

    regression = fit_ridge(X, y)
    return {
        'feature_keywords': feature_keywords,
        'feature_names': feature_names,
        'regression': regression,
    }


# ------------------------------------------------------------------------------
# STATISTICS FOR REPORT
# ------------------------------------------------------------------------------

def compute_cost_stats(cards):
    """Compute per-cost-level stat distributions for unit cards."""
    by_cost = defaultdict(list)
    for card in cards:
        if card['power'] is not None and card['health'] is not None:
            by_cost[card['cost']].append(card)

    rows = []
    for cost in sorted(by_cost.keys()):
        bucket = by_cost[cost]
        if len(bucket) < 2:
            continue
        powers = [c['power'] for c in bucket]
        healths = [c['health'] for c in bucket]
        phs = [p + h for p, h in zip(powers, healths)]
        n = len(bucket)
        rows.append({
            'cost': cost,
            'count': n,
            'avg_power': round(sum(powers) / n, 1),
            'avg_health': round(sum(healths) / n, 1),
            'avg_ph': round(sum(phs) / n, 1),
            'min_power': min(powers),
            'max_power': max(powers),
            'min_health': min(healths),
            'max_health': max(healths),
        })
    return rows


def compute_keyword_freq(cards):
    """Compute most common keywords per cost tier."""
    by_cost = defaultdict(list)
    for card in cards:
        by_cost[card['cost']].append(card)

    result = {}
    for cost, bucket in sorted(by_cost.items()):
        if len(bucket) < 5:
            continue
        kw_counts = defaultdict(int)
        for card in bucket:
            for kw in card['keywords']:
                kw_counts[kw] += 1
        top = sorted(kw_counts.items(), key=lambda x: -x[1])[:5]
        result[cost] = [(kw, count, round(100 * count / len(bucket)))
                        for kw, count in top]
    return result


def find_outliers(cards, sigma=1.5):
    """Find stat-weak cards (P+H more than sigma std devs below mean for their cost)."""
    by_cost = defaultdict(list)
    for card in cards:
        if card['power'] is not None and card['health'] is not None:
            by_cost[card['cost']].append(card)

    outliers = []
    for cost, bucket in by_cost.items():
        if len(bucket) < 5:
            continue
        phs = [c['power'] + c['health'] for c in bucket]
        mean_ph = sum(phs) / len(phs)
        variance = sum((x - mean_ph) ** 2 for x in phs) / len(phs)
        std_ph = math.sqrt(variance) if variance > 0 else 0
        if std_ph == 0:
            continue

        for card, ph in zip(bucket, phs):
            if ph < mean_ph - sigma * std_ph:
                outliers.append({
                    'card': card,
                    'cost': cost,
                    'ph': ph,
                    'mean_ph': round(mean_ph, 1),
                    'std_ph': round(std_ph, 1),
                })
    return outliers


# ------------------------------------------------------------------------------
# REPORT GENERATION
# ------------------------------------------------------------------------------

REPORT_ARENA_ORDER = ['Space', 'Ground', 'Character', 'Mission', 'Resource']


def generate_report(output_path=None):
    """Generate the full cost curve report and save to markdown + JSON."""
    print("Loading card database...")
    all_cards = load_cards()
    by_arena = group_by_arena(all_cards)

    print(f"Loaded {len(all_cards)} cards. Building regression models...")
    models = {}
    for arena, cards in by_arena.items():
        m = build_model(cards)
        if m:
            models[arena] = m
            reg = m['regression']
            print(f"  {arena}: {reg['n']} unit cards, R^2={reg['r_squared']:.3f}, alpha={reg['alpha']:.3f}")

    # Determine output paths
    if output_path is None:
        output_path = os.path.join(SCRIPT_DIR, "cost_curves.md")
    json_path = os.path.splitext(output_path)[0] + ".json"

    lines = ["# SWTCG Card Cost Reference\n"]
    lines.append(f"Generated from {len(all_cards)} cards (excluding Subordinates).\n")
    lines.append("Model: Ridge regression with 5-fold CV alpha selection. "
                 "Interaction terms (power x keyword) added for Accuracy, Critical Hit, Fury.\n")
    lines.append("---\n")

    other_arenas = [a for a in by_arena if a not in REPORT_ARENA_ORDER]
    for arena in REPORT_ARENA_ORDER + other_arenas:
        if arena not in by_arena:
            continue
        cards = by_arena[arena]
        lines.append(f"\n## {arena} ({len(cards)} cards)\n")

        # Regression model summary
        if arena in models:
            reg = models[arena]['regression']
            feature_names = models[arena]['feature_names']
            coefficients = reg['coefficients']

            lines.append(
                f"**Regression model** (Ridge) — n={reg['n']}, "
                f"R^2={reg['r_squared']:.3f}, RMSE={reg['rmse']:.2f}, "
                f"alpha={reg['alpha']:.3f}\n"
            )
            lines.append("```")
            lines.append(f"{'Predictor':<26}  {'Coeff':>8}")
            lines.append("-" * 37)
            lines.append(f"{'Constant':<26}  {reg['intercept']:>8.3f}")
            for name, coef in zip(feature_names, coefficients):
                display_name = _format_feature_name(name)
                lines.append(f"{display_name:<26}  {coef:>8.3f}")
            lines.append("```")
            lines.append(
                "\n_Note: Ridge coefficients are regularized toward zero. "
                "Interaction terms (power x keyword) capture scaling effects._\n"
            )
        else:
            lines.append("_Insufficient unit data for regression model._\n")

        # Cost curve table
        stats = compute_cost_stats(cards)
        if stats:
            lines.append("**Cost curve:**\n")
            lines.append("```")
            lines.append(f"{'Cost':>4} | {'N':>4} | {'Avg P':>5} | {'Avg H':>5} | {'Avg P+H':>7} | P range | H range")
            lines.append("-" * 58)
            for row in stats:
                lines.append(
                    f"{row['cost']:>4} | {row['count']:>4} | "
                    f"{row['avg_power']:>5} | {row['avg_health']:>5} | "
                    f"{row['avg_ph']:>7} | "
                    f"{row['min_power']}-{row['max_power']:<4} | "
                    f"{row['min_health']}-{row['max_health']}"
                )
            lines.append("```\n")

        # Keyword frequency
        kw_freq = compute_keyword_freq(cards)
        if kw_freq:
            lines.append("**Keyword frequency by cost tier:**\n")
            lines.append("```")
            for cost, freqs in sorted(kw_freq.items()):
                kw_str = ", ".join(f"{kw} ({pct}%)" for kw, _, pct in freqs)
                lines.append(f"Cost {cost:>2}: {kw_str}")
            lines.append("```\n")

        # Outliers
        outliers = find_outliers(cards)
        if outliers:
            lines.append("**Stat-weak cards** (P+H > 1.5 SD below cost-tier mean -- likely have significant abilities):\n")
            lines.append("```")
            for o in sorted(outliers, key=lambda x: (x['cost'], x['ph'])):
                c = o['card']
                flag = " [BANNED]" if c['is_banned'] else ""
                lines.append(
                    f"Cost {o['cost']:>2}: {c['name']} [{c['set']}]{flag}"
                    f"  P={c['power']}, H={c['health']} (mean P+H={o['mean_ph']})"
                )
                if c['text']:
                    preview = c['text'][:80] + "..." if len(c['text']) > 80 else c['text']
                    lines.append(f"         \"{preview}\"")
            lines.append("```\n")

    report_text = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nReport written to: {output_path}")

    # Write JSON for machine use
    json_data = {
        'total_cards': len(all_cards),
        'arena_models': {
            arena: {
                'n': m['regression']['n'],
                'r_squared': m['regression']['r_squared'],
                'rmse': m['regression']['rmse'],
                'alpha': m['regression']['alpha'],
                'intercept': m['regression']['intercept'],
                'features': dict(zip(m['feature_names'], m['regression']['coefficients'])),
                'feature_keywords': m['feature_keywords'],
            }
            for arena, m in models.items()
        }
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    print(f"JSON data written to: {json_path}")

    return models


# ------------------------------------------------------------------------------
# ESTIMATE MODE
# ------------------------------------------------------------------------------

def parse_keywords_arg(keywords_str):
    """Parse '--keywords "Accuracy 1, Critical Hit 2, Armor"' into a dict."""
    if not keywords_str:
        return {}
    result = {}
    for part in keywords_str.split(','):
        part = part.strip()
        if not part:
            continue
        m = re.match(r'^(.+?)\s+([+-]?\d+(?:\.\d+)?)\s*$', part)
        if m:
            result[m.group(1).strip()] = float(m.group(2))
        else:
            result[part] = 1  # Boolean keyword
    return result


def normalize_arena(arena_str):
    """Normalize arena type string to canonical form."""
    primary = arena_str.split('/')[0].strip().lower()
    for a in ['Space', 'Ground', 'Character', 'Mission', 'Resource']:
        if primary == a.lower():
            return a
    return arena_str.split('/')[0].strip().title()


def _format_feature_name(name):
    """Format a feature name for display in estimate/report output."""
    if name.startswith('power*'):
        kw = name[6:]
        return f"{kw} (x power)"
    return name


def estimate_cost(arena_type, power, health, keywords_dict, freeform_count, army_count,
                  prevention_ceiling, prevention_count, prevention_force_cost,
                  protect_ceiling, protect_force_cost,
                  retaliate_ceiling, retaliate_force_cost,
                  ambush_ceiling, ambush_force_cost,
                  is_unique, arenas, models):
    """Estimate build cost given card parameters.

    Returns estimate dict or None if no model available.
    """
    primary = normalize_arena(arena_type)

    if primary not in models or models[primary] is None:
        print(f"No model available for arena: {primary}")
        available = [a for a in models if models[a] is not None]
        if available:
            print(f"Available arenas: {', '.join(sorted(available))}")
        return None

    model = models[primary]
    reg = model['regression']
    feature_keywords = model['feature_keywords']
    feature_names = model['feature_names']
    coefficients = reg['coefficients']

    _always_show = {
        'power', 'health', 'freeform_count', 'army_count',
        'prevention_ceiling', 'prevention_count', 'prevention_force_cost',
        'protect_ceiling', 'protect_force_cost',
        'retaliate_ceiling', 'retaliate_force_cost',
        'ambush_ceiling', 'ambush_force_cost',
        'is_unique', 'multi_arena',
    }

    # Build feature value lookup
    features = {
        'power': power,
        'health': health,
        'freeform_count': freeform_count,
        'army_count': army_count,
        'prevention_ceiling':    prevention_ceiling,
        'prevention_count':      prevention_count,
        'prevention_force_cost': prevention_force_cost,
        'protect_ceiling':       protect_ceiling,
        'protect_force_cost':    protect_force_cost,
        'retaliate_ceiling':     retaliate_ceiling,
        'retaliate_force_cost':  retaliate_force_cost,
        'ambush_ceiling':        ambush_ceiling,
        'ambush_force_cost':     ambush_force_cost,
        'is_unique': 1 if is_unique else 0,
        'multi_arena': arenas - 1,
    }
    for kw in feature_keywords:
        features[kw] = keywords_dict.get(kw, 0)
    # Interaction terms: power * keyword_value
    for kw in POWER_INTERACTION_KEYWORDS:
        interaction_name = f'power*{kw}'
        if interaction_name in feature_names:
            features[interaction_name] = power * keywords_dict.get(kw, 0)

    # Predict with per-factor breakdown
    prediction = reg['intercept']
    breakdown = [('Base (intercept)', reg['intercept'], '')]

    for name, coef in zip(feature_names, coefficients):
        val = features.get(name, 0)
        contribution = coef * val
        prediction += contribution
        if val != 0 or name in _always_show:
            breakdown.append((name, contribution, f"{coef:+.3f} x {val}"))

    interval = 1.96 * reg['rmse']

    return {
        'prediction': prediction,
        'low': prediction - interval,
        'high': prediction + interval,
        'breakdown': breakdown,
        'r_squared': reg['r_squared'],
        'rmse': reg['rmse'],
        'n': reg['n'],
        'alpha': reg['alpha'],
        'arena': primary,
    }


def print_estimate(result, similar_cards=None):
    """Print cost estimate with per-factor breakdown and nearby cards."""
    print(f"\nEstimated build cost: {result['prediction']:.1f}  "
          f"(95% interval: {max(1, result['low']):.1f}-{result['high']:.1f})")
    print(f"Model: {result['arena']} units  "
          f"(n={result['n']}, R^2={result['r_squared']:.3f}, "
          f"RMSE={result['rmse']:.2f}, alpha={result['alpha']:.3f})\n")

    print("Factor breakdown:")
    total = 0
    for name, contrib, formula in result['breakdown']:
        total += contrib
        display_name = _format_feature_name(name) if name != 'Base (intercept)' else name
        if name == 'Base (intercept)':
            print(f"  {display_name:<30} {contrib:>+7.2f}")
        else:
            print(f"  {display_name:<30} {contrib:>+7.2f}   ({formula})")
    print(f"  {'-' * 42}")
    print(f"  {'Predicted':<30} {total:>7.1f}")

    if similar_cards:
        print("\nNearest existing cards for reference:")
        _print_card_list(similar_cards, n=5)


# ------------------------------------------------------------------------------
# SET RANKINGS MODE
# ------------------------------------------------------------------------------

def compute_set_residuals(all_cards, models):
    """Compute per-card (predicted - actual) residuals for all cards with a valid model.

    Multi-arena cards use their primary (first-listed) arena's model.

    Returns list of dicts: {set, name, arena, actual, predicted, residual}.
    """
    results = []
    for card in all_cards:
        arenas = card.get('arenas', [])
        if not arenas:
            continue
        primary = arenas[0]
        if primary not in models or models[primary] is None:
            continue
        # Skip cards with variable (*) stats — model training also excludes these
        if card['power'] is None or card['health'] is None:
            continue

        model = models[primary]
        reg = model['regression']
        feature_names = model['feature_names']
        feature_keywords = model['feature_keywords']
        coefficients = reg['coefficients']

        power = card['power'] or 0
        health = card['health'] or 0
        features = {
            'power': power,
            'health': health,
            'freeform_count': card['freeform_count'],
            'army_count': card['army_count'],
            'prevention_ceiling':    card['prevention_ceiling'],
            'prevention_count':      card['prevention_count'],
            'prevention_force_cost': card['prevention_force_cost'],
            'protect_ceiling':       card['protect_ceiling'],
            'protect_force_cost':    card['protect_force_cost'],
            'retaliate_ceiling':     card['retaliate_ceiling'],
            'retaliate_force_cost':  card['retaliate_force_cost'],
            'ambush_ceiling':        card['ambush_ceiling'],
            'ambush_force_cost':     card['ambush_force_cost'],
            'is_unique': 1 if card['is_unique'] else 0,
            'multi_arena': card['arena_count'] - 1,
        }
        for kw in feature_keywords:
            features[kw] = card['keywords'].get(kw, 0)
        for kw in POWER_INTERACTION_KEYWORDS:
            interaction_name = f'power*{kw}'
            if interaction_name in feature_names:
                features[interaction_name] = power * card['keywords'].get(kw, 0)

        prediction = reg['intercept']
        for name, coef in zip(feature_names, coefficients):
            prediction += coef * features.get(name, 0)

        results.append({
            'set': card['set'],
            'name': card['name'],
            'arena': primary,
            'actual': card['cost'],
            'predicted': prediction,
            'residual': prediction - card['cost'],
        })
    return results


def print_set_rankings(residuals):
    """Print sets ranked by mean residual (predicted - actual).

    Positive mean = cards are undercosted relative to stats/abilities = stronger set.
    """
    by_set = {}
    for r in residuals:
        by_set.setdefault(r['set'], []).append(r['residual'])

    set_stats = []
    for set_code, resids in by_set.items():
        n = len(resids)
        mean = sum(resids) / n
        if n > 1:
            variance = sum((x - mean) ** 2 for x in resids) / (n - 1)
            sd = math.sqrt(variance)
        else:
            sd = 0.0
        set_name = SETS.get(set_code, {})
        if isinstance(set_name, dict):
            set_name = set_name.get('name', set_code)
        if not set_name:
            set_name = set_code
        set_stats.append({
            'code': set_code,
            'name': set_name,
            'n': n,
            'mean': mean,
            'sd': sd,
            'min': min(resids),
            'max': max(resids),
        })

    set_stats.sort(key=lambda x: x['mean'], reverse=True)

    print("Set Rankings by Card Strength  (predicted - actual build cost)")
    print("Positive = undercosted relative to stats/abilities (stronger set)\n")
    header = f"{'Rank':>4}  {'Code':<6}  {'Set Name':<42}  {'n':>4}  {'Mean':>6}  {'SD':>5}  {'Min':>5}  {'Max':>5}"
    print(header)
    print("-" * len(header))
    for i, s in enumerate(set_stats, 1):
        flag = " *" if s['n'] < 5 else ""
        print(
            f"{i:>4}  {s['code']:<6}  {s['name'][:42]:<42}  {s['n']:>4}  "
            f"{s['mean']:>+6.2f}  {s['sd']:>5.2f}  {s['min']:>+5.2f}  {s['max']:>+5.2f}{flag}"
        )

    if any(s['n'] < 5 for s in set_stats):
        print("\n* fewer than 5 cards with valid predictions")


# ------------------------------------------------------------------------------
# SIMILAR CARDS MODE
# ------------------------------------------------------------------------------

def _arena_norm_stats(arena_cards):
    """Compute std dev of power and health for normalization."""
    unit_cards = [c for c in arena_cards if c['power'] is not None and c['health'] is not None]
    if len(unit_cards) < 2:
        return 1.0, 1.0
    powers = [c['power'] for c in unit_cards]
    healths = [c['health'] for c in unit_cards]
    mean_p = sum(powers) / len(powers)
    mean_h = sum(healths) / len(healths)
    var_p = sum((x - mean_p) ** 2 for x in powers) / len(powers)
    var_h = sum((x - mean_h) ** 2 for x in healths) / len(healths)
    return math.sqrt(var_p) if var_p > 0 else 1.0, math.sqrt(var_h) if var_h > 0 else 1.0


def find_similar_cards(arena_cards, power, health, keywords_dict=None,
                       cost=None, cost_range=None, n=10):
    """Find existing cards most similar by normalized stat distance.

    If keywords_dict provided, returns (same_kw, overlap_kw, no_kw) tuple.
    Otherwise returns flat sorted list.
    """
    std_p, std_h = _arena_norm_stats(arena_cards)

    scored = []
    for card in arena_cards:
        if card['power'] is None or card['health'] is None:
            continue
        if cost is not None and card['cost'] != cost:
            continue
        if cost_range is not None and not (cost_range[0] <= card['cost'] <= cost_range[1]):
            continue
        dp = (card['power'] - power) / std_p
        dh = (card['health'] - health) / std_h
        dist = math.sqrt(dp * dp + dh * dh)
        scored.append((card, dist))

    scored.sort(key=lambda x: x[1])

    if not keywords_dict:
        return scored[:n]

    query_kws = set(keywords_dict.keys())
    same_kw, overlap_kw, no_kw = [], [], []
    for card, dist in scored:
        card_kws = set(card['keywords'].keys())
        if card_kws == query_kws:
            same_kw.append((card, dist))
        elif card_kws & query_kws:
            overlap_kw.append((card, dist))
        else:
            no_kw.append((card, dist))

    return same_kw[:n], overlap_kw[:n], no_kw[:n]


def _print_card_list(cards_with_dist, n=10):
    """Print a list of (card, distance) tuples."""
    for i, (card, dist) in enumerate(cards_with_dist[:n], 1):
        flag = " [BANNED]" if card['is_banned'] else ""
        multi = (f" [{'/'.join(card['arenas'])}]"
                 if card['arena_count'] > 1 else "")
        print(f"  {i:>2}. {card['name']} [{card['set']}]{flag}{multi}")
        print(f"      Cost: {card['cost']}  P={card['power']}  H={card['health']}  dist={dist:.2f}")
        if card['text']:
            preview = card['text'][:72] + "..." if len(card['text']) > 72 else card['text']
            print(f"      \"{preview}\"")


def print_similar(results, power, health, arena, keywords_dict=None, n=10):
    """Print similar card search results."""
    header = f"Cards similar to: {arena} P={power} H={health}"
    if keywords_dict:
        kw_str = ", ".join(
            f"{k} {int(v)}" if v != 1 and v == int(v) else
            (f"{k} {v}" if v != 1 else k)
            for k, v in keywords_dict.items()
        )
        header += f"  [{kw_str}]"
    print(f"\n{header}")
    print("-" * 60)

    if isinstance(results, tuple):
        same_kw, overlap_kw, no_kw = results
        if same_kw:
            print("\n=== Same keywords ===")
            _print_card_list(same_kw, n)
        if overlap_kw:
            print("\n=== Overlapping keywords ===")
            _print_card_list(overlap_kw, n)
        if no_kw:
            print(f"\n=== Stat-similar, no keyword overlap (pure stat baseline) ===")
            _print_card_list(no_kw, n)
        if not any([same_kw, overlap_kw, no_kw]):
            print("  No matching cards found.")
    else:
        if results:
            _print_card_list(results, n)
        else:
            print("  No matching cards found.")


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SWTCG Card Cost Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python costAnalyzer.py --report
  python costAnalyzer.py --report --output my_report.md

  python costAnalyzer.py --estimate --type Space --power 4 --health 3 \\
      --keywords "Accuracy 1, Shields 1"

  python costAnalyzer.py --estimate --type Ground/Character --power 5 --health 5 \\
      --keywords "Armor" --arenas 2 --freeform 1

  python costAnalyzer.py --estimate --type Character --power 5 --health 5 \\
      --keywords "Evade 2" --army 1 --unique \\
      --prevention-ceiling 2 --prevention-force-cost 1

  python costAnalyzer.py --estimate --type Ground --power 4 --health 4 \\
      --keywords "Accuracy 1, Retaliate 3" --unique \\
      --retaliate-ceiling 3 --retaliate-force-cost 2

  python costAnalyzer.py --similar --type Character --power 6 --health 6
  python costAnalyzer.py --similar --type Ground --power 4 --health 4 --cost 5
  python costAnalyzer.py --similar --type Space --power 3 --health 2 \\
      --keywords "Accuracy 1" --cost-range 3 6 --n 15

  python costAnalyzer.py --rank-sets
        """
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--report', action='store_true',
                      help='Generate full cost curve report')
    mode.add_argument('--estimate', action='store_true',
                      help='Estimate build cost for a new card')
    mode.add_argument('--similar', action='store_true',
                      help='Find similar existing cards by stat distance')
    mode.add_argument('--rank-sets', action='store_true',
                      help='Rank all sets by card strength (mean predicted - actual cost)')

    parser.add_argument('--output', metavar='FILE',
                        help='Output path for --report (default: cost_curves.md)')
    parser.add_argument('--type', metavar='TYPE',
                        help='Arena type: Space, Ground, Character, Space/Ground, etc.')
    parser.add_argument('--power', type=int, metavar='N', help='Card power')
    parser.add_argument('--health', type=int, metavar='N', help='Card health')
    parser.add_argument('--keywords', metavar='STR',
                        help='Keywords as "Accuracy 1, Shields 1, Armor"')
    parser.add_argument('--freeform', type=int, default=0, metavar='N',
                        help='Number of freeform (non-keyword) ability clauses (default: 0)')
    parser.add_argument('--army', type=int, default=0, metavar='N',
                        help='Number of "Each of your X" / "Each of your other X" clauses (default: 0)')
    parser.add_argument('--unique', action='store_true',
                        help='Card is unique (has a version letter, e.g. Luke Skywalker (A))')
    parser.add_argument('--prevention-ceiling', type=float, default=0.0, metavar='N',
                        help='Sum of self-prevention values (Evade+Deflect+Absorb+Persuade) (default: 0)')
    parser.add_argument('--prevention-count', type=int, default=0, metavar='N',
                        help='Number of distinct self-prevention keyword types (e.g. 2 for Evade+Deflect) (default: 0)')
    parser.add_argument('--prevention-force-cost', type=float, default=0.0, metavar='N',
                        help='Total Force cost of self-prevention activations (default: 0)')
    parser.add_argument('--protect-ceiling', type=float, default=0.0, metavar='N',
                        help='Protect value (damage prevented to allies) (default: 0)')
    parser.add_argument('--protect-force-cost', type=float, default=0.0, metavar='N',
                        help='Force cost of Protect activations (default: 0)')
    parser.add_argument('--retaliate-ceiling', type=float, default=0.0, metavar='N',
                        help='Sum of Retaliate values (default: 0)')
    parser.add_argument('--retaliate-force-cost', type=float, default=0.0, metavar='N',
                        help='Force cost of Retaliate activations (default: 0)')
    parser.add_argument('--ambush-ceiling', type=float, default=0.0, metavar='N',
                        help='Sum of Ambush values (default: 0)')
    parser.add_argument('--ambush-force-cost', type=float, default=0.0, metavar='N',
                        help='Force cost of Ambush activations (default: 0)')
    parser.add_argument('--arenas', type=int, default=1, metavar='N',
                        help='Number of arenas the card counts toward (default: 1)')
    parser.add_argument('--cost', type=int, metavar='N',
                        help='Filter --similar results by exact build cost')
    parser.add_argument('--cost-range', nargs=2, type=int, metavar=('MIN', 'MAX'),
                        help='Filter --similar results by cost range')
    parser.add_argument('--n', type=int, default=10, metavar='N',
                        help='Number of --similar results to show (default: 10)')

    args = parser.parse_args()

    # -- Report mode -----------------------------------------------------------
    if args.report:
        generate_report(args.output)
        return

    # -- Rank-sets mode --------------------------------------------------------
    if args.rank_sets:
        print("Loading card database...")
        all_cards = load_cards()
        by_arena = group_by_arena(all_cards)
        print(f"Loaded {len(all_cards)} cards.\n")
        print("Building regression models (Ridge with CV)...")
        models = {}
        for arena, cards in by_arena.items():
            m = build_model(cards)
            if m:
                models[arena] = m
        residuals = compute_set_residuals(all_cards, models)
        print(f"Computed residuals for {len(residuals)} cards across {len(set(r['set'] for r in residuals))} sets.\n")
        print_set_rankings(residuals)
        return

    # -- Validate shared args for estimate/similar -----------------------------
    if not args.type:
        parser.error("--type is required")
    if args.power is None:
        parser.error("--power is required")
    if args.health is None:
        parser.error("--health is required")

    keywords_dict = parse_keywords_arg(args.keywords)

    print("Loading card database...")
    all_cards = load_cards()
    by_arena = group_by_arena(all_cards)
    print(f"Loaded {len(all_cards)} cards.\n")

    primary = normalize_arena(args.type)

    # -- Estimate mode ---------------------------------------------------------
    if args.estimate:
        print("Building regression models (Ridge with CV)...")
        models = {}
        for arena, cards in by_arena.items():
            m = build_model(cards)
            if m:
                models[arena] = m

        result = estimate_cost(
            args.type, args.power, args.health,
            keywords_dict, args.freeform, args.army,
            args.prevention_ceiling, args.prevention_count, args.prevention_force_cost,
            args.protect_ceiling, args.protect_force_cost,
            args.retaliate_ceiling, args.retaliate_force_cost,
            args.ambush_ceiling, args.ambush_force_cost,
            args.unique, args.arenas,
            models,
        )
        if result is None:
            return

        # Find a few similar cards to show alongside the estimate
        arena_cards = by_arena.get(primary, [])
        similar = find_similar_cards(arena_cards, args.power, args.health, n=5)
        if isinstance(similar, tuple):
            similar = similar[0] + similar[1] + similar[2]

        print_estimate(result, similar_cards=similar[:5])

    # -- Similar mode ----------------------------------------------------------
    elif args.similar:
        arena_cards = by_arena.get(primary, [])
        if not arena_cards:
            print(f"No cards found for arena: {primary}")
            available = sorted(by_arena.keys())
            print(f"Available arenas: {', '.join(available)}")
            return

        cost_range = tuple(args.cost_range) if args.cost_range else None
        results = find_similar_cards(
            arena_cards, args.power, args.health,
            keywords_dict=keywords_dict if keywords_dict else None,
            cost=args.cost,
            cost_range=cost_range,
            n=args.n,
        )
        print_similar(results, args.power, args.health, primary,
                      keywords_dict=keywords_dict if keywords_dict else None,
                      n=args.n)


if __name__ == "__main__":
    main()
