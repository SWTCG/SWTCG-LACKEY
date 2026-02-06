import discord
from discord.ext import commands, tasks
from discord import app_commands
import glob
import io
import requests
import random as pyrandom
from datetime import time, datetime
import urllib.request
import os
from rapidfuzz import fuzz, process
from SWTCG import Card, getCardFromLine, SETS, COSTLESS_TYPES, loadAllSets

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

IGNORED_SETS = ["HELP.txt", "START.txt"]
PT_BRANCH = "master"
TARGET_CHANNEL_ID = "1445637658163282083"
POST_TIME = time(14, 0)
SETS_FOLDER = os.path.join(SCRIPT_DIR, "..", "starwars", "sets")
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set.")

ALL_CARDS = []
CARDS_BY_SET = {}
NORMALIZED_NAMES = {}  # normalized name -> Card


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


def find_close_matches(query: str, limit: int = 5) -> list[tuple[Card, int]]:
    """Find cards with names closest to the query.

    Returns list of (Card, score) tuples sorted by score descending.
    """
    normalized_query = normalize_name(query)

    # Use rapidfuzz process.extract with token_set_ratio for best partial matching
    matches = process.extract(
        normalized_query,
        NORMALIZED_NAMES.keys(),
        scorer=fuzz.token_set_ratio,
        limit=limit
    )

    results = []
    for normalized_name, score, _ in matches:
        card = NORMALIZED_NAMES[normalized_name]
        results.append((card, score))

    return results

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
# @tasks.loop(seconds=30)
async def dailyPost():
    # if datetime.now().weekday() != 6:  # 0 = Monday
    #     return  
    channel = client.get_channel(int(TARGET_CHANNEL_ID))
    if channel is None:
        print("Channel not found!")
        return

    if not ALL_CARDS:
        print("No cards loaded!")
        return

    card = pyrandom.choice(ALL_CARDS)
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


def getColor(card):
    if card.side == 'L':
        return discord.Color.blue()
    elif card.side == 'D':
        return discord.Color.red()
    elif card.side == 'N':
        return 0xD2B58C
    elif card.side == 'Y':
        return 0x006400


@client.command()
async def random(ctx, setCode: str = None):
    if not ALL_CARDS:
        print("No cards loaded!")
        return

    if setCode:
        setCode = setCode.upper()
        cards = CARDS_BY_SET.get(setCode)

        if not cards:
            await ctx.send(f"I'm terribly sorry, but I don't recognize that set code: `{setCode}`.\n")
            return
    else:
        cards = ALL_CARDS

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
    if not ALL_CARDS:
        await interaction.response.send_message("No cards loaded!", ephemeral=True)
        return

    if set_code:
        set_code = set_code.upper()
        cards = CARDS_BY_SET.get(set_code)
        if not cards:
            await interaction.response.send_message(
                f"I don't recognize that set code: `{set_code}`.",
                ephemeral=True
            )
            return
    else:
        cards = ALL_CARDS

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


def loadAllCards():
    """Load all cards from TSV set files, skipping Subordinate cards."""
    global ALL_CARDS, CARDS_BY_SET, NORMALIZED_NAMES

    ALL_CARDS, CARDS_BY_SET = loadAllSets(SETS_FOLDER, skipSubordinates=True, ignoredFiles=IGNORED_SETS)

    NORMALIZED_NAMES = {}
    for card in ALL_CARDS:
        normalized = normalize_name(card.name)
        NORMALIZED_NAMES[normalized] = card

    print(f"Loaded {len(ALL_CARDS)} valid cards from {len(CARDS_BY_SET)} sets (after filtering).")

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

# def findCardInSet(cardName, setCode):
#   filepath = "/home/devon/dev/SWTCG-LACKEY/starwars/sets/" + setCode + ".txt"
#   print("Starting search in " + filepath)
#   with io.open(filepath, "r", encoding='latin1') as setFile:
#     card = findCardInSetFile(cardName, setFile)
#     if card == None:
#       print("Couldn't find card in " + filepath)
#     return card

class CardNotFoundError(Exception):
    """Raised when a card cannot be found, with optional suggestions."""

    def __init__(self, query: str, suggestions: list[tuple[Card, int]] = None):
        self.query = query
        self.suggestions = suggestions or []
        super().__init__(f"Card not found: {query}")


def findCard(cardName: str) -> Card:
    """Find a card by name with fuzzy matching fallback.

    Tries normalized exact match first, then fuzzy matching.
    Raises CardNotFoundError with suggestions if no good match is found.
    """
    # Try normalized exact match
    normalized = normalize_name(cardName)
    if normalized in NORMALIZED_NAMES:
        return NORMALIZED_NAMES[normalized]

    # Fuzzy match - find close matches
    matches = find_close_matches(cardName, limit=5)

    # If top match is very good (>= 90), return it directly
    if matches and matches[0][1] >= 90:
        print(f"Fuzzy matched '{cardName}' to '{matches[0][0].name}' (score: {matches[0][1]})")
        return matches[0][0]

    # Otherwise raise with suggestions
    print(f"Couldn't find card '{cardName}' in loaded cards.")
    raise CardNotFoundError(cardName, matches)


def findKeyword(keyword):
    keywords_path = os.path.join(SCRIPT_DIR, "keywords.txt")
    with io.open(keywords_path, "r", encoding='latin1') as keywordFile:
        for line in keywordFile:
            entry = line.split('\t')
            print("checking " + entry[0])
            if entry[0].casefold() == keyword.casefold():
                return entry[1]
    print("Couldn't find keyword in file.")
    raise Exception("Keyword not found")

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


def getCardUrl(cardName):
    card = findCard(cardName)
    return card.getImageUrl()

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
            suggestion_list = "\n".join(f"• {card.name}" for card, score in e.suggestions[:5])
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
            suggestion_list = "\n".join(f"• {card.name}" for card, score in e.suggestions[:5])
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
            suggestion_list = "\n".join(f"• {card.name}" for card, score in e.suggestions[:5])
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
            suggestion_list = "\n".join(f"• {card.name}" for card, score in e.suggestions[:5])
            await ctx.send(f"I couldn't find a card named **{e.query}**. Did you mean:\n{suggestion_list}")
        else:
            await ctx.send("I'm terribly sorry, but I can't find a card with that name.")
    except Exception as e:
        print(e)
        await ctx.send("I'm terribly sorry, but I can't find a card with that name. Perhaps you should double check your spelling?")

client.run(TOKEN)