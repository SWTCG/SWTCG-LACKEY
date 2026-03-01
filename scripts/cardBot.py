import argparse
import io
import os
import random as pyrandom
import re
from datetime import time

from rapidfuzz import fuzz, process
from SWTCG import Card, getCardFromLine, SETS, COSTLESS_TYPES, loadAllSets

# Matches trailing version specifier in user queries: "luke a", "vader b2"
VERSION_SPECIFIER_RE = re.compile(r'^(.+?)\s+([a-zA-Z][0-9]?)$')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Fuzzy matching thresholds
MIN_TOKEN_MATCH = 70    # Minimum fuzzy token match % to count as coverage
AMBIGUITY_THRESHOLD = 5.0  # Scores within this range are considered similar
MIN_MATCH_SCORE = 80.0    # Minimum score to auto-return

IGNORED_SETS = ["HELP.txt", "START.txt"]
PT_BRANCH = "master"
TARGET_CHANNEL_ID = "1445637658163282083"
POST_TIME = time(14, 0)
SETS_FOLDER = os.path.join(SCRIPT_DIR, "..", "starwars", "sets")

ALL_CARDS = []
NORMALIZED_NAMES = {}  # normalized name -> Card
RANDOM_CARDS = []  # Excludes subordinates
RANDOM_CARDS_BY_SET = {}  # Excludes subordinates


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
    # Increase limit when searching with version to ensure we get all versions
    stage1_limit = limit * 10 if target_version else limit * 4
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
    if normalized in NORMALIZED_NAMES:
        return NORMALIZED_NAMES[normalized]

    # Fuzzy match - find close matches
    matches = find_close_matches(cardName, limit=5)
    if not matches:
        raise CardNotFoundError(cardName, [])

    top_score = matches[0][1]

    # Find matches with similar scores
    similar = [m for m in matches if top_score - m[1] < AMBIGUITY_THRESHOLD]

    if len(similar) > 1:
        # Multiple similar matches - show only the tied ones for disambiguation
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

    if cardType not in COSTLESS_TYPES:
        details.append(f"{bold('Cost:')} {card.buildCost}")

    if card.isUnit:
        stats = f"{bold('Stats:')} {card.speed}/{card.power}/{card.health}"
        details.append(stats)

    details.append(f"{bold('Game Text:')} {card.cardText}")

    if card.usage:
        details.append(f"{bold('Usage Notes:')} {card.usage}")

    return "\n".join(details)


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


def run_bot_mode():
    import discord
    from discord.ext import commands, tasks
    from discord import app_commands
    import requests

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

    @client.event
    async def on_ready():
        if getattr(client, "started", False):
            return

        client.started = True
        loadAllCards()
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
                    "What do you think about it? Have you ever used it in a deck before?",
          color=color
        )

        embed.set_image(url=card.getImageUrl())
        await channel.send(embed=embed)

    @dailyPost.before_loop
    async def before_dailyPost():
        await client.wait_until_ready()

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

        await ctx.send(embed=embed)

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
            await ctx.send(embed=embed)
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

    client.run(TOKEN)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SWTCG Discord Bot")
    parser.add_argument("--test", action="store_true", help="Run in local test mode (no Discord)")
    args, _ = parser.parse_known_args()
    if args.test:
        run_test_mode()
    else:
        run_bot_mode()
