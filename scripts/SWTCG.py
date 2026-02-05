import os
import io

SETS = {"AOTC": "Attack of the Clones", "SR": "Sith Rising", "ANH": "A New Hope", "BOY": "Battle of Yavin", "JG": "Jedi Guardians", "ESB": "The Empire Strikes Back",
"RAS": "Rogues and Scoundrels", "PM": "The Phantom Menace", "ROTJ": "Return of the Jedi", "ROTS": "Revenge of the Sith", "FOTR": "Fall of the Republic",
"SAV": "Scum and Villainy", "BOE": "Battle of Endor", "RAW": "The Clone Wars: Republic at War", "ION": "Invasion of Naboo", "BOH": "Battle of Hoth", "BH": "Legacy of the Force: Bounty Hunters",
"MAND": "Legacy of the Force: Mandalorians", "SITH": "Legacy of the Force: Sith", "SMUG": "Legacy of the Force: Smugglers", "JEDI": "Legacy of the Force: Jedi", "RO2": "Rule of Two",
"TOR": "The Old Republic", "CWSO": "The Clone Wars: Separatist Offensive", "RS": "Rogue Squadron", "ER": "Empire Rising", "EE": "Empire Eternal", "AGD": "The Clone Wars: A Galaxy Divided",
"TDT": "The Dark Times", "CAD": "Clones and Droids", "TFA": "The Force Awakens", "VP": "The New Jedi Order: Vector Prime", "TAL": "The Old Republic: Tales and Legends",
"SBS": "The New Jedi Order: Star by Star", "DAN": "The Old Republic: Days and Nights", "BL": "The Clone Wars: Battle Lines", "RO": "Rogue One",
"TEN": "Tenth Anniversary", "BOSB": "Battle of Starkiller Base", "TLJ": "The Last Jedi", "SOR": "Spark of Rebellion", "BF": "Battlefront", "JK": "Jedi Knight",
"TUF": "The New Jedi Order: The Unifying Force", "BOC": "Battle of Crait", "SOLO": "Solo: A Star Wars Story", "KAE": "The Old Republic: Knights and Exiles",
"TM": "The Mandalorian", "15TH": "15th Anniversary", "TROS": "The Rise of Skywalker", "AAA": "Apprentices and Assassins", "FOR": "Fires of Rebellion", 
"BOTS": "Battle of the Sarlacc", "TMW": "The Mandalorian Way", "BAE": "Battle At Exegol", "BOBF": "The Book of Boba Fett", "ALTA": "A Long Time Ago", "UNION": "Union", "OBWN": "Obi-Wan Kenobi", "IA": "Imperial Assault",
"EAW": "Empire at War", "BEP": "Boonta Eve Podrace", "GPC": "Galactic Podracing Circuit", "WAE": "Doctor Aphra: Worst Among Equals", "VV1": "Visions Volume 1", "VV2": "Visions Volume 2",
"VDR": "Darth Vader: Shadows and Secrets", "HWN": "Halloween", "MAM": "Make A Mando", "LEG": "Legacy",
"HELP": "Help Cards", "START": "Starter Decks"}

# Card types that don't have build costs
COSTLESS_TYPES = ["Battle", "Event", "Subordinate", "Reminder"]

# Rarity code to name mapping
RARITIES = {"R": "Rare", "U": "Uncommon", "C": "Common", "P": "Promo", "S": "Subordinate"}

# Rarity name to code mapping (reverse of RARITIES)
RARITY_CODES = {"Rare": "R", "Uncommon": "U", "Common": "C", "Promo": "P", "Subordinate": "S"}

# Side name to code mapping
SIDES = {"Light": "L", "Dark": "D", "Neutral": "N", "Yuuzhan Vong": "Y"}

# Valid build cost layer names in PSD templates
VALID_BUILD_COSTS = [
    'Multi-arena build', 'Multi-Arena Build',
    'Space build', 'Space Build',
    'Ground build', 'Ground Build',
    'Character build', 'Character Build',
    'Resource Build', 'Trap Build', 'Campaign Build',
    'Mission Build', 'Trait Build', 'Skill Build', 'Equipment Build'
]


def isUnit(typeline):
    """Check if a typeline represents a unit (Space, Ground, Character, or Subordinate)."""
    tl = typeline.lower()
    return (tl.startswith("space") or
            tl.startswith("ground") or
            tl.startswith("character") or
            tl.startswith("subordinate"))


def parseTypeline(typeline):
    """Parse a typeline into (cardType, subtype).

    Examples:
        "Character - Jedi" -> ("Character", "Jedi")
        "Space - Starfighter" -> ("Space", "Starfighter")
        "Battle" -> ("Battle", "")
        "Event" -> ("Event", "")

    Returns:
        Tuple of (cardType, subtype) with proper title casing
    """
    typeline = typeline.lower().strip()

    # Types without subtypes
    for costlessType in COSTLESS_TYPES:
        if typeline.startswith(costlessType.lower()):
            return (costlessType, "")

    # Also check for Mission and Resource which don't have subtypes
    if typeline.startswith("mission") or typeline.startswith("resource"):
        return (typeline.title(), "")

    # Types with subtypes (separated by dash)
    dash_pos = typeline.find("-")
    if dash_pos != -1:
        cardType = typeline[:dash_pos].strip().title()
        subtype = typeline[dash_pos + 1:].strip().title().replace("\r", " ")
        return (cardType, subtype)

    # No dash found, return as-is
    return (typeline.title(), "")


def getSideCode(sideName):
    """Get the single-letter side code from a side name.

    Args:
        sideName: Full side name (e.g., "Light", "Dark", "Neutral", "Yuuzhan Vong")

    Returns:
        Single letter code (L, D, N, Y) or None if not found
    """
    return SIDES.get(sideName)


def getRarityCode(rarityName):
    """Get the single-letter rarity code from a rarity name.

    Args:
        rarityName: Full rarity name (e.g., "Common", "Rare")

    Returns:
        Single letter code (C, U, R, P, S) or None if not found
    """
    return RARITY_CODES.get(rarityName)


def isCostless(typeline):
    """Check if a card type doesn't have a build cost.

    Args:
        typeline: The card's typeline

    Returns:
        True if the card type has no build cost (Event, Battle, Subordinate, etc.)
    """
    tl = typeline.lower().strip()
    for costlessType in COSTLESS_TYPES:
        if tl.startswith(costlessType.lower()):
            return True
    return False


def cleanGameText(text):
    """Clean game text from PSD layers by removing flavor text and normalizing characters."""
    # Remove flavor text (everything after double line break)
    flavourPos = text.find("\r\r")
    if flavourPos != -1:
        text = text[:flavourPos]
    # Normalize special characters
    text = (text.replace("\r", " ")
                .replace("§", "->")
                .replace('<', '')
                .replace('"', '"')
                .replace('"', '"')
                .replace("'", "'")
                .replace("½", "Tap"))
    return text


def loadSetFile(path, skipSubordinates=False):
    """Load cards from a set file with automatic encoding detection.

    Args:
        path: Path to the set file
        skipSubordinates: If True, skip Subordinate cards

    Returns:
        List of Card objects
    """
    cards = []

    # Try UTF-8 first, fall back to latin1/cp1252
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="latin1") as f:
                lines = f.read().splitlines()
        except UnicodeDecodeError:
            with open(path, "r", encoding="cp1252") as f:
                lines = f.read().splitlines()

    if not lines:
        return cards

    # Skip header row
    for line in lines[1:]:
        if not line.strip():
            continue
        try:
            card = getCardFromLine(line)
            if skipSubordinates and card.typeline == "Subordinate":
                continue
            cards.append(card)
        except (IndexError, KeyError):
            continue  # Skip malformed lines

    return cards


def loadAllSets(folder, skipSubordinates=False, ignoredFiles=None):
    """Load all cards from set files in a folder.

    Args:
        folder: Path to folder containing set files
        skipSubordinates: If True, skip Subordinate cards
        ignoredFiles: List of filenames to skip (e.g., ["HELP.txt", "START.txt"])

    Returns:
        Tuple of (allCards, cardsBySet) where cardsBySet is a dict keyed by set code
    """
    if ignoredFiles is None:
        ignoredFiles = []

    allCards = []
    cardsBySet = {}

    for filename in os.listdir(folder):
        if filename in ignoredFiles or not filename.endswith(".txt"):
            continue

        fullPath = os.path.join(folder, filename)
        cards = loadSetFile(fullPath, skipSubordinates=skipSubordinates)

        for card in cards:
            allCards.append(card)
            cardsBySet.setdefault(card.setCode, []).append(card)

    return allCards, cardsBySet


class Card:
    def __init__(self):
        self.name = "[name]"
        self.setCode = "[SET]"
        self.setName = "[Set Full Name]"
        self.imageFrag = "[imageFrag]"
        self.side = "[side]"
        self.typeline = "[type]"
        self.subtype = "[subtype]"
        self.cardType = ""  # Parsed from typeline (e.g., "Character", "Space")
        self.buildCost = "[buildCost]"
        self.speed = "[speed]"
        self.power = "[power]"
        self.health = "[health]"
        self.rarity = "[rarity]"
        self.number = "[number]"
        self.usage = "[usage]"
        self.cardText = "[game text]"
        self.script = "[script]"
        self.classification = "[classification]"
        self.uniqueLetter = ""
        self.isUnit = False
        self.isPromo = False
        self.sideCount = 0
        self.rarityCount = 0

    def getImageUrl(self):
        return f"https://raw.githubusercontent.com/SWTCG/SWTCG-LACKEY/refs/heads/release/official/starwars/sets/setimages/{self.setCode}/{self.imageFrag}.jpg"

    def setTypeline(self, typeline):
        """Parse and set typeline, cardType, subtype, and isUnit.

        Also handles costless types (sets buildCost to "") and
        Subordinates (sets buildCost="" and rarity="S").
        For non-units, clears speed/power/health.
        """
        self.typeline = typeline.lstrip(" ")
        self.cardType, self.subtype = parseTypeline(self.typeline)
        self.isUnit = isUnit(self.typeline)

        # Subordinates have special handling
        if self.cardType == "Subordinate":
            self.buildCost = ""
            self.rarity = "S"
        elif isCostless(self.typeline):
            self.buildCost = ""

        # Non-units don't have combat stats
        if not self.isUnit:
            self.speed = ""
            self.power = ""
            self.health = ""

    def setSide(self, sideName):
        """Set side from name (e.g., "Light" -> "L"). Tracks sideCount."""
        code = getSideCode(sideName)
        if code:
            self.side = code
            self.sideCount += 1

    def setRarity(self, rarityName):
        """Set rarity from name (e.g., "Rare" -> "R"). Tracks rarityCount."""
        code = getRarityCode(rarityName)
        if code:
            self.rarity = code
            self.rarityCount += 1

    def setCardName(self, name, uniqueLetter=None):
        """Set card name, optionally appending unique letter and promo suffix.

        Args:
            name: The base card name
            uniqueLetter: Optional unique letter (A, B, etc.) to append
        """
        self.name = name.replace("'", "'").rstrip('\r\n').rstrip()
        if uniqueLetter:
            self.uniqueLetter = uniqueLetter.upper()
            self.name = f"{self.name} ({self.uniqueLetter})"
        if self.isPromo:
            self.name = f"{self.name} (Promo)"

    def validate(self, imageFrag=""):
        """Validate card fields and log issues.

        Args:
            imageFrag: Image fragment name for error messages

        Returns:
            List of validation error strings
        """
        issues = []

        if self.typeline in ("[type]", "[typeline]"):
            issues.append(f"{imageFrag}: typeline - no correctly named layer found")

        if self.isUnit:
            if self.speed == "[speed]":
                issues.append(f"{imageFrag}: speed - no correctly named layer found")
            if self.power == "[power]":
                issues.append(f"{imageFrag}: power - no correctly named layer found")
            if self.health == "[health]":
                issues.append(f"{imageFrag}: health - no correctly named layer found")

        if self.buildCost == "[buildCost]":
            issues.append(f"{imageFrag}: buildCost - no correctly named layer found")

        if self.cardText == "[game text]":
            issues.append(f"{imageFrag}: game text - no correctly named layer found")

        if self.number == "[number]":
            issues.append(f"{imageFrag}: number - no correctly named layer found")

        if self.sideCount == 0 or self.sideCount > 1:
            issues.append(f"{imageFrag}: side - {self.sideCount} layers marked visible")
            self.side = "[side]"

        if self.rarityCount > 1 or (self.rarityCount == 0 and self.rarity != "S"):
            issues.append(f"{imageFrag}: rarity - {self.rarityCount} layers marked visible")
            self.rarity = "[rarity]"

        for issue in issues:
            print(f"{self.name} -- {issue}")

        return issues

    def validateNumberMatch(self, fileNameNumber, imageFrag=""):
        """Validate that card number matches filename number.

        Args:
            fileNameNumber: Number extracted from filename
            imageFrag: Image fragment name for error messages
        """
        if fileNameNumber != "promo" and fileNameNumber != "sub" and self.number != fileNameNumber:
            print(f"{self.name} -- {imageFrag}: number on card ({self.number}) doesn't match number in file name ({fileNameNumber})")

    def validateUniqueLetter(self, imageFrag=""):
        """Validate that unique letter matches filename suffix."""
        if self.uniqueLetter and self.uniqueLetter != imageFrag[-len(self.uniqueLetter):]:
            print(f"{self.name} -- {imageFrag}: unique letter ({self.uniqueLetter}) doesn't match file name suffix ({imageFrag[-len(self.uniqueLetter):]})")

    def toSetFileRow(self, setCode, classification=""):
        """Generate dict for pandas DataFrame row.

        Args:
            setCode: The set code (e.g., "LEG")
            classification: Optional classification value

        Returns:
            Dict with all columns for set file DataFrame
        """
        return {
            'Name': self.name,
            'Set': setCode,
            'ImageFile': self.imageFrag,
            'Side': self.side,
            'Type': self.cardType,
            'Subtype': self.subtype,
            'Cost': self.buildCost,
            'Speed': self.speed,
            'Power': self.power,
            'Health': self.health,
            'Rarity': self.rarity,
            'Number': self.number,
            'Usage': self.usage if self.usage != "[usage]" else "",
            'Text': self.cardText,
            'Script': self.script if self.script != "[script]" else "",
            'Classification': classification
        }


def getCardFromLine(rawLine):
    line = rawLine.split('\t')
    card = Card()
    card.name = line[0]
    card.setCode = line[1]
    card.setName = SETS[card.setCode]
    card.imageFrag = line[2]
    card.side = line[3]
    card.typeline = line[4]  # Note: In set files this is just the type (e.g., "Character")
    card.cardType = line[4]  # Same as typeline for set file parsing
    card.subtype = line[5]
    card.buildCost = line[6]
    card.speed = line[7]
    card.power = line[8]
    card.health = line[9]
    card.rarity = line[10]
    card.number = line[11]
    card.usage = line[12]
    card.cardText = line[13]
    card.script = line[14]
    card.classification = line[15]
    card.isUnit = isUnit(card.typeline)
    return card