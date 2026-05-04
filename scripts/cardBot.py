import argparse
import asyncio
import io
import os
import random as pyrandom
import re
import requests
import sys
from datetime import time
from urllib.parse import urlencode

from rapidfuzz import fuzz, process
from SWTCG import Card, getCardFromLine, SETS, COSTLESS_TYPES, isCostless, loadAllSets

# Matches trailing version specifier in user queries: "luke a", "vader b2"
VERSION_SPECIFIER_RE = re.compile(r'^(.+?)\s+([a-zA-Z][0-9]?)$')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Fuzzy matching thresholds
MIN_TOKEN_MATCH = 70    # Minimum fuzzy token match % to count as coverage
AMBIGUITY_THRESHOLD = 5.0  # Scores within this range are considered similar
MIN_MATCH_SCORE = 80.0    # Minimum score to auto-return

IGNORED_SETS = ["HELP.txt", "START.txt"]
PT_BRANCH = "LOTA"
WEB_APP_URL = "https://warshawd.github.io/swtcg-dice-calculator/"
TARGET_CHANNEL_ID = "1445637658163282083"
POST_TIME = time(14, 0)
SETS_FOLDER = os.path.join(SCRIPT_DIR, "..", "starwars", "sets")

DECK_DB_URL = os.getenv('DECK_DB_URL', 'http://localhost:8000')
BOT_API_KEY = os.getenv('BOT_API_KEY', '')
# Number keycap emojis 1-5 mapped to rating values
RATING_EMOJIS = {
    '\u0031\ufe0f\u20e3': 1,
    '\u0032\ufe0f\u20e3': 2,
    '\u0033\ufe0f\u20e3': 3,
    '\u0034\ufe0f\u20e3': 4,
    '\u0035\ufe0f\u20e3': 5,
}

ALL_CARDS = []
NORMALIZED_NAMES = {}  # normalized name -> Card
RANDOM_CARDS = []  # Excludes subordinates
RANDOM_CARDS_BY_SET = {}  # Excludes subordinates

NUM_TRIALS_BOT = 250_000

SIDE_COLORS = {
    'L': '#3498DB',  # blue  (matches discord.Color.blue())
    'D': '#E74C3C',  # red   (matches discord.Color.red())
    'N': '#D2B58C',  # tan
    'Y': '#006400',  # green (matches 0x006400 in getColor)
}

COMBAT_KW_RE = {
    'accuracy':    re.compile(r'^Accuracy\s+([+-]?\d+)', re.IGNORECASE),
    'criticalHit': re.compile(r'^Critical\s+Hit\s+(\d+)', re.IGNORECASE),
    'fury':        re.compile(r'^Fury\s+(\d+)', re.IGNORECASE),
    'lucky':       re.compile(r'^Lucky\s+(\d+)', re.IGNORECASE),
    'parry':       re.compile(r'^Parry\s+(\d+)', re.IGNORECASE),
    'shields':     re.compile(r'^Shields\s+(\d+)', re.IGNORECASE),
}
ARMOR_RE = re.compile(r'^Armor\b', re.IGNORECASE)


def normalize_name(name: str) -> str:
    """Normalize a card name for fuzzy matching.

    Removes parentheses, apostrophes, hyphens, and extra whitespace.
    Converts to lowercase.
    """
    # Remove parentheses but keep their contents
    name = name.replace('(', '').replace(')', '')
    # Remove apostrophes and hyphens
    name = name.replace("'", '').replace('-', ' ')
    # Collapse whitespace and lowercase
    name = ' '.join(name.lower().split())
    return name


def parse_version_query(query: str) -> tuple[str, str | None]:
    """Parse query for trailing version specifier.

    Detects when user query ends with a single letter or letter+digit,
    indicating they want a specific card version.

    Examples:
        "luke a" -> ("luke", "A")
        "vader b2" -> ("vader", "B2")
        "yoda" -> ("yoda", None)
        "protocol droid" -> ("protocol droid", None)
    """
    match = VERSION_SPECIFIER_RE.match(query.strip())
    if not match:
        return (query, None)

    base, version = match.group(1), match.group(2).upper()

    # Version must be: single letter A-Z, or letter + digit 2-9
    if not re.match(r'^[A-Z][2-9]?$', version):
        return (query, None)

    # Base query must be at least 2 chars (avoid "x a" being parsed)
    if len(base.strip()) < 2:
        return (query, None)

    return (base, version)


def version_sort_key(version: str) -> int:
    """Convert version letter to sortable integer.

    A=1, B=2... Z=26, A2=27, B2=28... Z2=52, A3=53, etc.
    Empty/None = 0 (sorts first).
    """
    if not version:
        return 0
    version = version.upper()
    letter_val = ord(version[0]) - ord('A') + 1
    if len(version) == 1:
        return letter_val
    digit = int(version[1])
    return (digit - 1) * 26 + letter_val


def calculate_composite_score(query: str, card_name: str,
                              target_version: str = None,
                              card_version: str = None) -> float:
    """Calculate a composite score for fuzzy matching.

    Combines four factors:
    - Coverage: How well query tokens match card tokens (fuzzy per-token matching)
    - Length ratio: Prefer shorter card names for short queries (weighted medium)
    - Fuzzy: Handle typos and partial matches (weighted lowest)
    - Version bonus: Boost exact version matches, penalize possessives
    """
    query_tokens = normalize_name(query).split()
    card_tokens = set(normalize_name(card_name).split())

    # Fuzzy coverage: for each query token, find best matching card token
    # Require minimum 70% match to count as a match (avoids "lightsaber" matching "skywalker" at 42%)
    if query_tokens and card_tokens:
        token_scores = []
        for qt in query_tokens:
            best_match = max(fuzz.ratio(qt, ct) for ct in card_tokens)
            # Only count matches above threshold
            token_scores.append(best_match / 100.0 if best_match >= MIN_TOKEN_MATCH else 0)
        coverage = sum(token_scores) / len(query_tokens)
    else:
        coverage = 0

    # Length ratio: slight preference for shorter cards (reduced weight - was causing issues)
    length_ratio = min(1.0, len(query_tokens) / len(card_tokens)) if card_tokens else 0

    # Fuzzy: overall string similarity for typo tolerance
    fuzzy = fuzz.WRatio(normalize_name(query), normalize_name(card_name)) / 100.0

    # Version matching bonus
    version_bonus = 0
    if target_version:
        if card_version == target_version:
            version_bonus = 50  # Strong boost for exact version match
        # Penalize possessives (equipment) when searching for character version
        if "'s " in card_name and card_version:
            version_bonus -= 30
        # Prefer non-promo when both exist with the same version letter
        if "(Promo)" in card_name:
            version_bonus -= 6

    # Weighted composite (coverage dominates, length ratio reduced from 10 to 5)
    return coverage * 100 + length_ratio * 5 + fuzzy + version_bonus


def find_close_matches(query: str, limit: int = 5) -> list[tuple[Card, float]]:
    """Find cards with names closest to the query using two-stage scoring.

    Stage 1: Fast initial candidates via rapidfuzz token_set_ratio
    Stage 2: Re-score with composite algorithm (version-aware)

    Returns list of (Card, score) tuples sorted by score desc, version asc.
    """
    # Parse version specifier from query (e.g., "luke a" -> base="luke", version="A")
    base_query, target_version = parse_version_query(query)
    normalized_query = normalize_name(base_query)

    # Stage 1: Fast initial candidates via rapidfuzz
    # Use token_set_ratio for better partial token matching (e.g., "luke a" -> "luke skywalker a")
    # For version queries, must be large enough to include ALL cards sharing the base name prefix
    # (e.g., Anakin alone has 78 cards) so nothing gets cut before stage2 version scoring.
    stage1_limit = 500 if target_version else limit * 4
    initial_matches = process.extract(
        normalized_query,
        NORMALIZED_NAMES.keys(),
        scorer=fuzz.token_set_ratio,
        limit=stage1_limit
    )

    # Stage 2: Re-score with composite algorithm (version-aware)
    results = []
    for norm_name, _, _ in initial_matches:
        card = NORMALIZED_NAMES[norm_name]
        score = calculate_composite_score(
            base_query, card.name,
            target_version, card.uniqueLetter
        )
        results.append((card, score))

    # Sort by score descending, then by version letter ascending for ties
    results.sort(key=lambda x: (-x[1], version_sort_key(x[0].uniqueLetter)))
    return results[:limit]


def loadAllCards():
    """Load all cards from TSV set files.

    ALL_CARDS includes all cards for direct lookups.
    RANDOM_CARDS excludes subordinates for random commands.
    """
    global ALL_CARDS, NORMALIZED_NAMES, RANDOM_CARDS, RANDOM_CARDS_BY_SET

    ALL_CARDS, _ = loadAllSets(SETS_FOLDER, skipSubordinates=False, ignoredFiles=IGNORED_SETS)

    NORMALIZED_NAMES = {}
    for card in ALL_CARDS:
        normalized = normalize_name(card.name)
        if normalized in NORMALIZED_NAMES:
            NORMALIZED_NAMES[normalized] = None  # Collision - fall through to fuzzy
        else:
            NORMALIZED_NAMES[normalized] = card

    # Build filtered lists for random commands (exclude subordinates)
    RANDOM_CARDS = [c for c in ALL_CARDS if c.typeline != "Subordinate"]
    RANDOM_CARDS_BY_SET = {}
    for card in RANDOM_CARDS:
        RANDOM_CARDS_BY_SET.setdefault(card.setCode, []).append(card)

    print(f"Loaded {len(ALL_CARDS)} cards from {len(RANDOM_CARDS_BY_SET)} sets ({len(RANDOM_CARDS)} for random).")


def bold(s):
    return "**" + s + "**"


def findCardInSetFile(cardName, setFile):
    first = True
    for line in setFile:
        if first:
            first = False
            continue
        card = getCardFromLine(line)
        if card.name.casefold() == cardName.casefold():
            print("Found! In " + card.setCode)
            return card
    return None


class CardNotFoundError(Exception):
    """Raised when a card cannot be found, with optional suggestions."""

    def __init__(self, query: str, suggestions: list[tuple[Card, float]] = None):
        self.query = query
        self.suggestions = suggestions or []
        super().__init__(f"Card not found: {query}")


def findCard(cardName: str) -> Card:
    """Find a card by name with fuzzy matching fallback.

    Tries normalized exact match first, then fuzzy matching with ambiguity detection.
    Raises CardNotFoundError with suggestions if no good match or ambiguous results.
    """
    # Try normalized exact match
    normalized = normalize_name(cardName)
    exact = NORMALIZED_NAMES.get(normalized)
    if exact is not None:
        return exact

    # Fuzzy match - find close matches
    matches = find_close_matches(cardName, limit=5)
    if not matches:
        raise CardNotFoundError(cardName, [])

    top_score = matches[0][1]

    # Find matches with similar scores
    similar = [m for m in matches if top_score - m[1] < AMBIGUITY_THRESHOLD]

    if len(similar) > 1 and top_score >= MIN_MATCH_SCORE:
        # Multiple high-confidence similar matches - show only the tied ones for disambiguation
        print(f"Ambiguous query '{cardName}': {len(similar)} similar matches")
        raise CardNotFoundError(cardName, similar)
    elif top_score >= MIN_MATCH_SCORE:
        print(f"Fuzzy matched '{cardName}' to '{matches[0][0].name}' (score: {top_score:.1f})")
        return matches[0][0]
    else:
        # Score too low - show suggestions
        print(f"Couldn't find card '{cardName}' in loaded cards (best score: {top_score:.1f})")
        raise CardNotFoundError(cardName, matches)


def findKeyword(keyword):
    keywords_path = os.path.join(SCRIPT_DIR, "keywords.txt")
    with io.open(keywords_path, "r", encoding='latin1') as keywordFile:
        for line in keywordFile:
            entry = line.split('\t')
            if entry[0].casefold() == keyword.casefold():
                return entry[1]
    print("Couldn't find keyword in file.")
    raise Exception("Keyword not found")


def processDetails(card: Card):
    details = []

    number_str = f" #{card.number}" if card.number else ""
    details.append(f"{bold(card.name)} - {card.setCode}{number_str}")

    cardType = card.typeline
    if card.subtype:
        cardType += f" - {card.subtype}"
    details.append(cardType)

    if not isCostless(card.typeline):
        details.append(f"{bold('Cost:')} {card.buildCost}")

    if card.isUnit:
        stats = f"{bold('Stats:')} {card.speed}/{card.power}/{card.health}"
        details.append(stats)

    details.append(f"{bold('Game Text:')} {card.cardText}")

    if card.usage:
        details.append(f"{bold('Usage Notes:')} {card.usage}")

    return "\n".join(details)


def getLuckyOrder(attackerSide, defenderSide):
    if attackerSide == 'D' and defenderSide != 'D': return 'a'
    if defenderSide == 'D' and attackerSide != 'D': return 'd'

    if attackerSide == 'Y' and defenderSide == 'L': return 'a'
    if defenderSide == 'Y' and attackerSide == 'L': return 'd'

    if attackerSide == 'N' and defenderSide == 'L': return 'a'
    if defenderSide == 'N' and attackerSide == 'L': return 'd'

    return 'a'


def extractCombatStats(card):
    """Extract combat keywords from card text by scanning clause-by-clause.

    Splits on '|' and uses re.match() so only clauses that *start* with a
    keyword are counted — avoiding false positives from ability text that
    merely references a keyword (e.g. 'Each of your units gets Accuracy 2').
    """
    stats = {
        'power':       int(card.power) if str(card.power).isdigit() else 0,
        'accuracy':    0,
        'criticalHit': 0,
        'fury':        0,
        'lucky':       0,
        'parry':       0,
        'shields':     0,
        'armor':       False,
    }
    for clause in (card.cardText or '').split('|'):
        clause = clause.strip()
        for key, pattern in COMBAT_KW_RE.items():
            m = pattern.match(clause)
            if m:
                stats[key] = int(m.group(1))
                break
        if ARMOR_RE.match(clause):
            stats['armor'] = True
    return stats


def buildWebAppUrl(power, accuracy, criticalHit, parry, fury, aLucky, dLucky,
                   shields, armor, order, name):
    params = {
        'power':      power,
        'accuracy':   accuracy,
        'crit':       criticalHit,
        'parry':      parry,
        'fury':       fury,
        'aLucky':     aLucky,
        'dLucky':     dLucky,
        'shields':    shields,
        'luckyOrder': order,
        'name':       name,
    }
    if armor:
        params['armor'] = '1'
    return WEB_APP_URL + '?' + urlencode(params)


def formatSimStats(power, accuracy, criticalHit, fury, aLucky, parry, shields, armor, dLucky):
    """Return (attacker_line, defender_line) strings summarising extracted stats.

    defender_line is None when there are no defensive keywords to show.
    """
    a_parts = [f"{power} power"]
    if accuracy != 0:
        a_parts.append(f"Acc {accuracy:d}")
    if criticalHit:
        a_parts.append(f"Crit {criticalHit}")
    if fury:
        a_parts.append(f"Fury {fury}")
    if aLucky:
        a_parts.append(f"Lucky {aLucky}")

    d_parts = []
    if armor:
        d_parts.append("Armor")
    if shields:
        d_parts.append(f"Shields {shields}")
    if parry:
        d_parts.append(f"Parry {parry}")
    if dLucky:
        d_parts.append(f"Lucky {dLucky}")

    return ", ".join(a_parts), (", ".join(d_parts) if d_parts else None)


def run_test_mode():
    """Interactive CLI for testing fuzzy matching."""
    print("Loading cards...")
    loadAllCards()
    print(f"Loaded {len(ALL_CARDS)} cards. Type queries or 'quit' to exit.\n")

    while True:
        try:
            query = input("Query> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        try:
            card = findCard(query)
            print(f"  Found: {card.name} ({card.setCode})")
        except CardNotFoundError as e:
            print(f"  Not found: {e.query}")
            if e.suggestions:
                print("  Suggestions:")
                for card, score in e.suggestions:
                    print(f"    {score:6.1f}  {card.name}")


def _card_from_embed(embed):
    """Extract a Card from a bot embed. Returns None if not a card embed.

    Card command embeds use card.name as the title directly.
    COTD/random embeds use "**card.name** - setName" in the description.
    """
    if embed.title:
        card = next((c for c in ALL_CARDS if c.name == embed.title), None)
        if card:
            return card
    if embed.description:
        m = re.match(r'^\*\*(.+?)\*\*', embed.description)
        if m:
            return next((c for c in ALL_CARDS if c.name == m.group(1)), None)
    return None


def _post_rating(discord_user_id, card_name, set_code, rating):
    """Synchronous — call via asyncio.to_thread."""
    try:
        r = requests.post(
            f'{DECK_DB_URL}/api/ratings',
            json={'discord_user_id': str(discord_user_id),
                  'card_name': card_name, 'set_code': set_code, 'rating': rating},
            headers={'X-Bot-API-Key': BOT_API_KEY},
            timeout=5
        )
        return r.json()
    except Exception as e:
        print(f'Rating API error: {e}')
        return None


def _delete_rating(discord_user_id, card_name, set_code):
    """Synchronous — call via asyncio.to_thread."""
    try:
        r = requests.delete(
            f'{DECK_DB_URL}/api/ratings',
            json={'discord_user_id': str(discord_user_id),
                  'card_name': card_name, 'set_code': set_code},
            headers={'X-Bot-API-Key': BOT_API_KEY},
            timeout=5
        )
        return r.json()
    except Exception as e:
        print(f'Rating delete API error: {e}')
        return None


def run_bot_mode():
    import discord
    from discord.ext import commands, tasks
    from discord import app_commands

    _DICE_CALC_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'swtcg-dice-calculator')
    sys.path.insert(0, _DICE_CALC_DIR)
    from damageCalculator import runSimulation, generatePlotBuffer

    def warmupKaleido():
        import plotly.graph_objects as go
        import plotly.io as pio
        pio.to_image(go.Figure(), format='png', width=1, height=1)

    async def simulate(power, accuracy, criticalHit, parry, fury, aLucky, dLucky,
                        shields, armor, order, name,
                        attacker_label=None, defender_label=None, color='#4a9eff'):
        """Run simulation and return (discord.File, discord.Embed)."""
        eff_power    = max(0, power - shields)
        eff_accuracy = accuracy - (1 if armor else 0)

        exp_dmg, _, _, _, damageDist, hitsDist = await asyncio.to_thread(
            runSimulation,
            power=eff_power, criticalHit=criticalHit, accuracy=eff_accuracy,
            parry=parry, fury=fury, aLucky=aLucky, dLucky=dLucky,
            order=order, numTrials=NUM_TRIALS_BOT
        )
        a_line, d_line = formatSimStats(power, accuracy, criticalHit, fury, aLucky,
                                        parry, shields, armor, dLucky)
        subtitle = a_line + (" -vs- " + d_line if d_line else "")
        buf = await asyncio.to_thread(generatePlotBuffer, damageDist, name, subtitle, color)
        url = buildWebAppUrl(power, accuracy, criticalHit, parry, fury, aLucky, dLucky,
                             shields, armor, order, name)

        lines = []
        if attacker_label:
            lines.append(f"⚔️ **{attacker_label}** — {a_line}")
        else:
            lines.append(f"⚔️ {a_line}")
        if defender_label:
            lines.append(f"🛡️ **{defender_label}**" + (f" — {d_line}" if d_line else ""))
        elif d_line:
            lines.append(f"🛡️ {d_line}")
        mode_hits = max(hitsDist, key=hitsDist.get)
        lines.append(f"Avg Damage: **{exp_dmg:.1f}**")
        lines.append(f"Mode Hits: **{mode_hits}**")
        lines.append(f"[Open in calculator ↗]({url})")

        file  = discord.File(buf, filename="sim.png")
        embed = discord.Embed(description="\n".join(lines), color=int(color.lstrip('#'), 16))
        embed.set_image(url="attachment://sim.png")
        return file, embed

    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN environment variable not set.")

    intents = discord.Intents.default()
    intents.message_content = True

    client = commands.Bot(
        command_prefix='!',
        intents=intents,
        allowed_installs=discord.app_commands.AppInstallationType(
            guild=True,
            user=True
        ),
        allowed_contexts=discord.app_commands.AppCommandContext(
            guild=True,
            dm_channel=True,
            private_channel=True  # Enables group DM support
        )
    )
    tree = client.tree

    def getColor(card):
        if card.side == 'L':
            return discord.Color.blue()
        elif card.side == 'D':
            return discord.Color.red()
        elif card.side == 'N':
            return 0xD2B58C
        elif card.side == 'Y':
            return 0x006400
        return discord.Color.default()

    @client.event
    async def on_ready():
        if getattr(client, "started", False):
            return

        client.started = True
        loadAllCards()
        asyncio.create_task(asyncio.to_thread(warmupKaleido))
        dailyPost.start()

        # Sync slash commands with Discord
        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

        print('SWTCG bot ready')

    @tasks.loop(time=POST_TIME)
    async def dailyPost():
        channel = client.get_channel(int(TARGET_CHANNEL_ID))
        if channel is None:
            print("Channel not found!")
            return

        if not RANDOM_CARDS:
            print("No cards loaded!")
            return

        card = pyrandom.choice(RANDOM_CARDS)
        color = getColor(card)
        embed = discord.Embed(
          title="Random Card of the Day!",
          description=f"**{card.name}** - {card.setName}\n\n"
                    "What do you think about it? Have you ever used it in a deck before?\n"
                    "React 1-5 to rate this card!",
          color=color
        )

        embed.set_image(url=card.getImageUrl())
        msg = await channel.send(embed=embed)
        _message_card_cache[msg.id] = card
        for emoji in RATING_EMOJIS:
            await msg.add_reaction(emoji)

    @dailyPost.before_loop
    async def before_dailyPost():
        await client.wait_until_ready()

    _message_card_cache = {}  # message_id -> Card
    _dm_sent_users = set()

    async def _get_card_for_reaction(payload):
        """Return the Card for a reaction payload using an in-memory cache with HTTP fallback."""
        card = _message_card_cache.get(payload.message_id)
        if card is not None:
            return card
        channel = client.get_channel(payload.channel_id)
        if channel is None:
            try:
                channel = await client.fetch_channel(payload.channel_id)
            except (discord.NotFound, discord.Forbidden):
                return None
        try:
            message = await channel.fetch_message(payload.message_id)
        except (discord.NotFound, discord.Forbidden):
            return None
        if not message.embeds:
            return None
        card = _card_from_embed(message.embeds[0])
        if card is not None:
            _message_card_cache[payload.message_id] = card
        return card

    async def _notify_unlinked(user_id):
        if user_id in _dm_sent_users:
            return
        _dm_sent_users.add(user_id)
        try:
            user = await client.fetch_user(user_id)
            await user.send(
                f"Hello! To save your card ratings, you need to log in with "
                f"your Discord account at: https://swtcg-deckdb.com"
                f"\n(This message is sent only once.)"
            )
        except Exception as e:
            print(f'Could not DM user {user_id}: {e}')

    @client.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == client.user.id:
            return
        emoji_str = str(payload.emoji)
        if emoji_str not in RATING_EMOJIS:
            return
        card = await _get_card_for_reaction(payload)
        if card is None:
            return
        result = await asyncio.to_thread(
            _post_rating, payload.user_id, card.name, card.setCode, RATING_EMOJIS[emoji_str])
        if result and not result.get('ok') and result.get('reason') == 'unlinked':
            await _notify_unlinked(payload.user_id)

    @client.event
    async def on_raw_reaction_remove(payload):
        if payload.user_id == client.user.id:
            return
        if str(payload.emoji) not in RATING_EMOJIS:
            return
        card = await _get_card_for_reaction(payload)
        if card is None:
            return
        await asyncio.to_thread(_delete_rating, payload.user_id, card.name, card.setCode)

    @client.command()
    async def random(ctx, setCode: str = None):
        if not RANDOM_CARDS:
            print("No cards loaded!")
            return

        if setCode:
            setCode = setCode.upper()
            cards = RANDOM_CARDS_BY_SET.get(setCode)

            if not cards:
                await ctx.send(f"I'm terribly sorry, but I don't recognize that set code: `{setCode}`.\n")
                return
        else:
            cards = RANDOM_CARDS

        card = pyrandom.choice(cards)
        color = getColor(card)

        if setCode:
            embed = discord.Embed(
                title=f"Random Card from {setCode}:",
                description=f"**{card.name}** - {card.setName}",
                color=color
            )
        else:
            embed = discord.Embed(
                title="Random Card:",
                description=f"**{card.name}** - {card.setName}",
                color=color
            )
        embed.set_image(url=card.getImageUrl())
        msg = await ctx.send(embed=embed)
        _message_card_cache[msg.id] = card

    @client.tree.command(name="random", description="Get a random card, optionally from a specific set.")
    @app_commands.describe(set_code="Optional set code to filter by (e.g., ANH, ROTJ)")
    async def slash_random(interaction: discord.Interaction, set_code: str = None):
        if not RANDOM_CARDS:
            await interaction.response.send_message("No cards loaded!", ephemeral=True)
            return

        if set_code:
            set_code = set_code.upper()
            cards = RANDOM_CARDS_BY_SET.get(set_code)
            if not cards:
                await interaction.response.send_message(
                    f"I don't recognize that set code: `{set_code}`.",
                    ephemeral=True
                )
                return
        else:
            cards = RANDOM_CARDS

        card = pyrandom.choice(cards)
        color = getColor(card)

        title = f"Random Card from {set_code}:" if set_code else "Random Card:"
        embed = discord.Embed(
            title=title,
            description=f"**{card.name}** - {card.setName}",
            color=color
        )
        embed.set_image(url=card.getImageUrl())
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        _message_card_cache[msg.id] = card

    @client.command()
    @commands.has_role(700748867104145478)
    async def pt(ctx, *args):
        try:
            setCode = args[0].upper()
            cardName = ' '.join(args[1:])
            print("New Request! Searching for playtesting card " + cardName + " in set " + setCode)
            setFileUrl = "https://raw.githubusercontent.com/SWTCG/SWTCG-LACKEY/refs/heads/" + PT_BRANCH + "/starwars/sets/" + setCode + ".txt"
            x = requests.get(setFileUrl)
            card = findCardInSetFile(cardName, io.StringIO(x.text))
            if card == None:
                raise Exception("Couldn't find card in " + setFileUrl)
            imageFrag = card.imageFrag
            url = "https://raw.githubusercontent.com/SWTCG/SWTCG-LACKEY/refs/heads/" + PT_BRANCH + "/starwars/sets/setimages/" + setCode + "/" + imageFrag + ".jpg"
            await ctx.send(url)
        except Exception as e:
            print(e)
            await ctx.send("I'm terribly sorry, but I can't find a card with that name. Perhaps you should double check your spelling?")

    @client.tree.command(name="keyword", description="Get the definition of a keyword ability.")
    @app_commands.describe(keyword="The keyword to search for")
    async def slashKeyword(interaction: discord.Interaction, keyword: str):
        try:
            print("New Request! Searching for keyword " + keyword)
            definition = findKeyword(keyword)
            await interaction.response.send_message(definition)
        except Exception as e:
            print(e)
            await interaction.response.send_message("I'm terribly sorry, but I can't find a keyword with that name. Perhaps you should double check your spelling?", ephemeral=True)

    @client.command()
    async def keyword(ctx, *, arg):
        try:
            print("New Request! Searching for keyword " + arg)
            definition = findKeyword(arg)
            await ctx.send(definition)
        except Exception as e:
            print(e)
            await ctx.send("I'm terribly sorry, but I can't find a keyword with that name. Perhaps you should double check your spelling?")

    @client.tree.command(name="details", description="Get the details of a card")
    @app_commands.describe(name="The card name to search for")
    async def slashDetails(interaction: discord.Interaction, name: str):
        try:
            print("New Request! Searching details for card " + name)
            card = findCard(name)
            details = processDetails(card)
            await interaction.response.send_message(details)
        except CardNotFoundError as e:
            print(e)
            if e.suggestions:
                suggestion_list = "\n".join(f"• {card.name}" for card, score in e.suggestions)
                await interaction.response.send_message(
                    f"I couldn't find a card named **{e.query}**. Did you mean:\n{suggestion_list}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "I'm terribly sorry, but I can't find a card with that name.",
                    ephemeral=True
                )
        except Exception as e:
            print(e)
            await interaction.response.send_message("I'm terribly sorry, but I can't find a card with that name. Perhaps you should double check your spelling?", ephemeral=True)

    @client.command()
    async def details(ctx, *, arg):
        try:
            print("New Request! Searching details for card " + arg)
            card = findCard(arg)
            details = processDetails(card)
            await ctx.send(details)
        except CardNotFoundError as e:
            print(e)
            if e.suggestions:
                suggestion_list = "\n".join(f"• {card.name}" for card, score in e.suggestions)
                await ctx.send(f"I couldn't find a card named **{e.query}**. Did you mean:\n{suggestion_list}")
            else:
                await ctx.send("I'm terribly sorry, but I can't find a card with that name.")
        except Exception as e:
            print(e)
            await ctx.send("I'm terribly sorry, but I can't find a card with that name. Perhaps you should double check your spelling?")

    @tree.command(name="card", description="Get the image for a card by name.")
    @app_commands.describe(name="The card name to search for")
    async def slash_card(interaction: discord.Interaction, name: str):
        try:
            print("New Request! Searching for card " + name)
            card = findCard(name)
            color = getColor(card)
            embed = discord.Embed(
                title=f"{card.name}",
                description=f"{card.setCode} #{card.number}",
                color=color
            )
            embed.set_image(url=card.getImageUrl())
            await interaction.response.send_message(embed=embed)
            msg = await interaction.original_response()
            _message_card_cache[msg.id] = card
        except CardNotFoundError as e:
            print(e)
            if e.suggestions:
                suggestion_list = "\n".join(f"• {card.name}" for card, score in e.suggestions)
                await interaction.response.send_message(
                    f"I couldn't find a card named **{e.query}**. Did you mean:\n{suggestion_list}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "I'm terribly sorry, but I can't find a card with that name.",
                    ephemeral=True
                )
        except Exception as e:
            print(e)
            await interaction.response.send_message("I'm terribly sorry, but I can't find a card with that name. Perhaps you should double check your spelling?", ephemeral=True)

    @client.command()
    async def card(ctx, *, arg):
        try:
            print("New Request! Searching for card " + arg)
            card = findCard(arg)
            color = getColor(card)
            embed = discord.Embed(
                title=f"{card.name}",
                description=f"{card.setCode} #{card.number}",
                color=color
            )
            embed.set_image(url=card.getImageUrl())
            msg = await ctx.send(embed=embed)
            _message_card_cache[msg.id] = card
        except CardNotFoundError as e:
            print(e)
            if e.suggestions:
                suggestion_list = "\n".join(f"• {card.name}" for card, score in e.suggestions)
                await ctx.send(f"I couldn't find a card named **{e.query}**. Did you mean:\n{suggestion_list}")
            else:
                await ctx.send("I'm terribly sorry, but I can't find a card with that name.")
        except Exception as e:
            print(e)
            await ctx.send("I'm terribly sorry, but I can't find a card with that name. Perhaps you should double check your spelling?")

    # ------------------------------------------------------------------ attack

    def parseAttackArg(arg):
        """Split 'Attacker vs Defender' into (attacker_name, defender_name|None)."""
        parts = re.split(r'\s+vs\s+', arg, maxsplit=1, flags=re.IGNORECASE)
        return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else None)

    async def runAttack(attacker_name, defender_name):
        attacker = findCard(attacker_name)
        if not attacker.isUnit:
            raise ValueError(f"{attacker.name} is not a unit.")
        defender = None
        if defender_name:
            defender = findCard(defender_name)
            if not defender.isUnit:
                raise ValueError(f"{defender.name} is not a unit.")

        a = extractCombatStats(attacker)
        d = extractCombatStats(defender) if defender else {}
        order = getLuckyOrder(attacker.side, defender.side if defender else 'N')
        name  = attacker.name + (f" vs {defender.name}" if defender else "")
        color = SIDE_COLORS.get(attacker.side, '#4a9eff')

        return await simulate(
            power=a['power'], accuracy=a['accuracy'], criticalHit=a['criticalHit'],
            parry=d.get('parry', 0), fury=a['fury'],
            aLucky=a['lucky'], dLucky=d.get('lucky', 0),
            shields=d.get('shields', 0), armor=d.get('armor', False),
            order=order, name=name,
            attacker_label=attacker.name,
            defender_label=defender.name if defender else None,
            color=color
        )

    @client.command()
    async def attack(ctx, *, arg):
        attacker_name, defender_name = parseAttackArg(arg)
        try:
            async with ctx.typing():
                file, embed = await runAttack(attacker_name, defender_name)
            await ctx.send(file=file, embed=embed)
        except CardNotFoundError as e:
            if e.suggestions:
                suggestion_list = "\n".join(f"• {c.name}" for c, _ in e.suggestions)
                await ctx.send(f"Couldn't find **{e.query}**. Did you mean:\n{suggestion_list}")
            else:
                await ctx.send(f"Couldn't find a card named **{e.query}**.")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @client.tree.command(name="attack", description="Simulate an attack between two cards.")
    @app_commands.describe(attacker="Attacking card name", defender="Defending card name (optional)")
    async def slash_attack(interaction: discord.Interaction, attacker: str, defender: str = None):
        await interaction.response.defer()
        try:
            file, embed = await runAttack(attacker, defender)
            await interaction.followup.send(file=file, embed=embed)
        except CardNotFoundError as e:
            if e.suggestions:
                suggestion_list = "\n".join(f"• {c.name}" for c, _ in e.suggestions)
                await interaction.followup.send(
                    f"Couldn't find **{e.query}**. Did you mean:\n{suggestion_list}", ephemeral=True)
            else:
                await interaction.followup.send(
                    f"Couldn't find a card named **{e.query}**.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    # ------------------------------------------------------------------ roll

    @client.command()
    async def roll(ctx, *args):
        try:
            params = {}
            for arg in args:
                if ':' in arg:
                    k, _, v = arg.partition(':')
                    params[k.lower()] = v

            power = int(params.get('power', 0))
            if power <= 0:
                await ctx.send("Please specify power: `!roll power:6`")
                return

            accuracy = int(params.get('accuracy', params.get('acc', 0)))
            crit     = int(params.get('crit', 0))
            fury     = int(params.get('fury', 0))
            parry    = int(params.get('parry', 0))
            shields  = int(params.get('shields', 0))
            armor    = params.get('armor', '').lower() in ('1', 'true', 'yes')
            alucky   = int(params.get('alucky', params.get('lucky', 0)))
            dlucky   = int(params.get('dlucky', 0))
            name     = params.get('name', f"Power {power}")

            async with ctx.typing():
                file, embed = await simulate(
                    power=power, accuracy=accuracy, criticalHit=crit,
                    parry=parry, fury=fury, aLucky=alucky, dLucky=dlucky,
                    shields=shields, armor=armor, order='a', name=name
                )
            await ctx.send(file=file, embed=embed)
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @client.tree.command(name="roll", description="Simulate an attack with custom stats.")
    @app_commands.describe(
        power="Attack dice (required)",
        accuracy="Accuracy modifier",
        crit="Critical Hit value",
        fury="Fury value",
        parry="Defender Parry",
        shields="Defender Shields",
        armor="Defender has Armor",
        alucky="Attacker Lucky",
        dlucky="Defender Lucky",
        name="Label for the chart"
    )
    async def slash_roll(interaction: discord.Interaction,
                         power: int,
                         accuracy: int = 0, crit: int = 0, fury: int = 0,
                         parry: int = 0, shields: int = 0, armor: bool = False,
                         alucky: int = 0, dlucky: int = 0,
                         name: str = None):
        await interaction.response.defer()
        try:
            file, embed = await simulate(
                power=power, accuracy=accuracy, criticalHit=crit,
                parry=parry, fury=fury, aLucky=alucky, dLucky=dlucky,
                shields=shields, armor=armor, order='a',
                name=name or f"Power {power}"
            )
            await interaction.followup.send(file=file, embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    client.run(TOKEN)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SWTCG Discord Bot")
    parser.add_argument("--test", action="store_true", help="Run in local test mode (no Discord)")
    args, _ = parser.parse_known_args()
    if args.test:
        run_test_mode()
    else:
        run_bot_mode()
