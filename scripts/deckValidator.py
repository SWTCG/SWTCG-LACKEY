"""
SWTCG Deck Validator
Usage: python deckValidator.py <deckfile.dek|deckfile.txt>

Validates a deck against SWTCG construction rules:
  - Minimum 60 cards (59 if a Resource card is in Supply/Sideboard/Outside the game)
  - Minimum 36 units (Space, Ground, Character — not Subordinate)
  - Minimum 12 of each arena type (Space, Ground, Character)
  - No arena may have more than 2x the units of any other arena
  - Max 4 copies of any card
  - Restricted cards (marked in Usage): max 1 copy
  - Banned cards (marked in Usage): not allowed anywhere (deck or outside sections)
  - Single primary side (Light, Dark, or Yuuzhan Vong) + Neutral allowed
    (applies to deck and outside sections — Events and Subordinates outside must also align)
  - All card names must exist in the set files

Input formats:
  .dek  — LackeyCCG XML deck format
  .txt  — LackeyCCG tab-separated text format (count<TAB>name)
"""

import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from SWTCG import loadAllSets, SIDES

SETS_FOLDER = os.path.join(SCRIPT_DIR, "..", "starwars", "sets")
IGNORED_SETS = ["HELP.txt"]

MIN_DECK_SIZE = 60
MIN_UNITS = 36
MIN_PER_ARENA = 12
MAX_COPIES = 4

UNIT_ARENAS = {"space", "ground", "character"}
SECTION_HEADERS = {"supply:", "sideboard:", "outside the game:"}
SIDE_NAMES = {code: name for name, code in SIDES.items()}  # e.g. {"L": "Light", ...}
PRIMARY_SIDES = {code for code in SIDE_NAMES if code != "N"}


def parseDekFile(path):
    """Parse a LackeyCCG .dek XML file.

    Returns:
        (deck_names, outside_names): card name lists (one entry per copy).
        deck_names  — cards in the Deck superzone.
        outside_names — cards in all other superzones (Supply, Sideboard, etc.).
    """
    tree = ET.parse(path)
    root = tree.getroot()
    deck_names = []
    outside_names = []
    for superzone in root.findall(".//superzone"):
        zone_name = superzone.get("name", "")
        target = deck_names if zone_name == "Deck" else outside_names
        for card in superzone.findall("card"):
            name_el = card.find("name")
            if name_el is not None and name_el.text:
                target.append(name_el.text.strip())
    return deck_names, outside_names


def parseTxtFile(path):
    """Parse a LackeyCCG .txt deck list.

    Format: count<TAB>card name
    Lines before the first section header go into deck_names.
    Lines in Supply:, Sideboard:, Outside the game: go into outside_names.

    Returns:
        (deck_names, outside_names): card name lists (one entry per copy).
    """
    encodings = ["utf-8", "latin1", "cp1252"]
    lines = None
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                lines = f.read().splitlines()
            break
        except UnicodeDecodeError:
            continue
    if lines is None:
        print(f"Error: could not decode {path}")
        sys.exit(1)

    deck_names = []
    outside_names = []
    in_outside = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower() in SECTION_HEADERS:
            in_outside = True
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0].strip().isdigit():
            count = int(parts[0].strip())
            name = parts[1].strip()
            target = outside_names if in_outside else deck_names
            target.extend([name] * count)

    return deck_names, outside_names


def parseDeck(path):
    """Detect format by extension and parse accordingly.

    Returns:
        (deck_names, outside_names): card name lists (one entry per copy).
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".dek":
        return parseDekFile(path)
    elif ext == ".txt":
        return parseTxtFile(path)
    else:
        print(f"Error: unsupported file extension '{ext}'. Expected .dek or .txt")
        sys.exit(1)


def getArenas(cardType):
    """Return arena type strings for a card type, handling multi-arena (e.g. 'Space/Ground')."""
    types = [t.strip() for t in cardType.split("/")]
    return [t for t in types if t.lower() in UNIT_ARENAS]


def isBanned(card):
    return "BANNED" in card.usage


def isRestricted(card):
    return "RESTRICTED" in card.usage


def checkCards(names, cardDb, label, deck_primary_side, errors, warnings):
    """Validate a list of card names (banned + side checks only; no copy/unit counting).

    Used for outside-the-deck sections. Modifies errors and warnings in place.

    Args:
        names: list of card name strings (one per copy)
        cardDb: dict of {name.lower(): Card}
        label: section label for error messages (e.g. "outside")
        deck_primary_side: the primary side already determined from the deck (or None)
        errors, warnings: lists to append messages to
    """
    counts = Counter(name.lower() for name in names)
    display_name = {}
    for name in names:
        key = name.lower()
        if key not in display_name:
            display_name[key] = name

    for key, count in counts.items():
        dname = display_name[key]
        card = cardDb.get(key)

        if card is None:
            warnings.append(f"  [UNKNOWN]     {dname} x{count} ({label}) — not found in any set file")
            continue

        if isBanned(card):
            usage = card.usage.strip()
            excerpt = usage[:80] + ("..." if len(usage) > 80 else "")
            errors.append(f"  [BANNED]      {dname} x{count} ({label}) — {excerpt}")

        if deck_primary_side and card.side in PRIMARY_SIDES and card.side != deck_primary_side:
            errors.append(
                f"  [SIDE]        {dname} x{count} ({label}) — "
                f"{SIDE_NAMES.get(card.side, card.side)} card in a "
                f"{SIDE_NAMES.get(deck_primary_side, deck_primary_side)} deck"
            )


def validate(deck_names, outside_names, cardDb):
    """Validate deck and outside cards against all construction rules.

    Args:
        deck_names: list of card name strings in the main deck (one per copy)
        outside_names: list of card name strings in Supply/Sideboard/Outside sections
        cardDb: dict of {name.lower(): Card}

    Returns:
        True if valid, False if any errors found.
    """
    errors = []
    warnings = []

    # --- Deck section ---
    counts = Counter(name.lower() for name in deck_names)
    display_name = {}
    for name in deck_names:
        key = name.lower()
        if key not in display_name:
            display_name[key] = name

    total_cards = len(deck_names)
    total_units = 0
    space_count = 0
    ground_count = 0
    char_count = 0
    sides_seen = set()

    for key, count in counts.items():
        dname = display_name[key]
        card = cardDb.get(key)

        if card is None:
            warnings.append(f"  [UNKNOWN]     {dname} x{count} — not found in any set file")
            continue

        if isBanned(card):
            usage = card.usage.strip()
            excerpt = usage[:80] + ("..." if len(usage) > 80 else "")
            errors.append(f"  [BANNED]      {dname} x{count} — {excerpt}")

        elif isRestricted(card) and count > 1:
            errors.append(f"  [RESTRICTED]  {dname} x{count} — max 1 copy allowed (restricted)")

        if count > MAX_COPIES:
            errors.append(f"  [COPIES]      {dname} x{count} — max {MAX_COPIES} copies allowed")

        if card.side in PRIMARY_SIDES:
            sides_seen.add(card.side)

        arenas = getArenas(card.cardType)
        if arenas:
            total_units += count
            if any(a.lower() == "space" for a in arenas):
                space_count += count
            if any(a.lower() == "ground" for a in arenas):
                ground_count += count
            if any(a.lower() == "character" for a in arenas):
                char_count += count

    # Determine deck primary side (used for outside validation below)
    deck_primary_side = next(iter(sides_seen)) if len(sides_seen) == 1 else None

    # --- Deck size ---
    # A Resource in any outside section allows 59 instead of 60
    has_outside_resource = any(
        cardDb.get(name.lower()) is not None and cardDb[name.lower()].cardType.lower() == "resource"
        for name in outside_names
    )
    min_size = MIN_DECK_SIZE - (1 if has_outside_resource else 0)
    if total_cards < min_size:
        note = " (Resource in outside sections allows 59)" if has_outside_resource else ""
        errors.append(f"  [SIZE]        Only {total_cards} cards (minimum {min_size}{note})")

    # --- Side restriction (deck) ---
    if len(sides_seen) > 1:
        mixed = ", ".join(SIDE_NAMES.get(s, s) for s in sorted(sides_seen))
        errors.append(f"  [SIDE]        Mixed primary sides in deck: {mixed}")

    # --- Unit minimums ---
    if total_units < MIN_UNITS:
        errors.append(f"  [UNITS]       Only {total_units} units (minimum {MIN_UNITS})")

    if space_count < MIN_PER_ARENA:
        errors.append(f"  [ARENA]       Only {space_count} Space units (minimum {MIN_PER_ARENA})")

    if ground_count < MIN_PER_ARENA:
        errors.append(f"  [ARENA]       Only {ground_count} Ground units (minimum {MIN_PER_ARENA})")

    if char_count < MIN_PER_ARENA:
        errors.append(f"  [ARENA]       Only {char_count} Character units (minimum {MIN_PER_ARENA})")

    # --- Arena balance ---
    arena_counts = {"Space": space_count, "Ground": ground_count, "Character": char_count}
    for a, b in [("Space", "Ground"), ("Space", "Character"), ("Ground", "Character")]:
        ca, cb = arena_counts[a], arena_counts[b]
        if cb > 0 and ca > cb * 2:
            errors.append(f"  [BALANCE]     {a} ({ca}) > 2× {b} ({cb})")
        elif ca > 0 and cb > ca * 2:
            errors.append(f"  [BALANCE]     {b} ({cb}) > 2× {a} ({ca})")

    # --- Outside sections (banned + side checks) ---
    if outside_names:
        checkCards(outside_names, cardDb, "outside", deck_primary_side, errors, warnings)

    # --- Print report ---
    print()
    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
        print()
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(w)
        print()

    outside_note = f" + {len(outside_names)} outside" if outside_names else ""
    print(
        f"Total cards: {total_cards}{outside_note}"
        f"  |  Units: {total_units}"
        f" (Space: {space_count}, Ground: {ground_count}, Character: {char_count})"
    )
    print()

    if errors:
        print(f"Result: INVALID ({len(errors)} error{'s' if len(errors) != 1 else ''}"
              + (f", {len(warnings)} warning{'s' if len(warnings) != 1 else ''}" if warnings else "")
              + ")")
        return False
    else:
        if warnings:
            print(f"Result: VALID ({len(warnings)} warning{'s' if len(warnings) != 1 else ''})")
        else:
            print("Result: VALID")
        return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python deckValidator.py <deckfile.dek|deckfile.txt>")
        sys.exit(1)

    deck_path = sys.argv[1]
    if not os.path.exists(deck_path):
        print(f"Error: file not found: {deck_path}")
        sys.exit(1)

    print(f"=== Deck Validator: {os.path.basename(deck_path)} ===")

    allCards, _ = loadAllSets(SETS_FOLDER, ignoredFiles=IGNORED_SETS)
    cardDb = {card.name.lower(): card for card in allCards}
    print(f"Loaded {len(allCards)} cards from set files.")

    deck_names, outside_names = parseDeck(deck_path)
    valid = validate(deck_names, outside_names, cardDb)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
