from psd_tools import PSDImage
import pandas as pd
import os
import glob
import re

from SWTCG import Card, VALID_BUILD_COSTS

# Segments that follow a line break but continue the PREVIOUS ability (not a new clause).
# Checked before the uppercase-start fallback that assumes a new clause.
_CONTINUATION_STARTERS = re.compile(
    r'^('
    r'If you do\b|'
    r"If you don't\b|"
    r'Or:|'             # "Or: ..." inside a "Choose one:" ability — may be alone on line or followed by space
    r'Play only\b|'     # "Play only when/during/once per turn"
    r'That (unit|Character|Space|Ground)\b|'
    r'It can\b|'
    r'You may play this\b|'
    r'For this attack\b|'
    r'->|'                  # cost/effect arrow split to start of line
    r'\*|'                  # pilot ability bullet — * separates abilities, no | needed
    r'Vong\b|'              # "Yuuzhan Vong" wrapped across lines
    r'Subordinate(?!s)'     # singular type descriptor mid-phrase (e.g. "put 1 X/Y/Z Name Subordinate into arena")
    r')'
)

# If the PREVIOUS segment ends with one of these, the next segment continues it.
# These words/symbols cannot grammatically end an ability clause in SWTCG card text.
_CONTINUATION_ENDERS = re.compile(
    r'('
    r'->$|'                         # cost/effect split across lines (anchored — avoids matching -> inside quoted abilities)
    r':$|'                          # "choose one:", "INSERT:", "Last Stand:", "Or:" alone
    r',$|'                          # comma-terminated stat list (e.g. "+2 power,")
    r'\bor$|\band$|\bthan$|'        # coordinating conjunctions / comparisons
    r'\bwith$|\bwithout$|'
    r'\bto$|\bthe$|\ba$|\ban$|'
    r'\bgets$|\bget$|\bloses$|\blose$|\bremove$|\badd$|\bplace$|\bput$|\btake$|\bcosts$|'
    r'\bher$|\bhis$|\bits$|\bthis$|'
    r'\bin$|\bon$|\bfor$|\bby$|\bfrom$|\binto$|\bagainst$|\buntil$|'
    r'\btimes$|\bhas$|\bhave$|'
    r'\byour$|'                         # possessive mid-phrase (e.g. "remove counters from your / Resource")
    r'\d/\d+$|'                         # stat block (cost/power/health) mid-phrase, e.g. "1 50/3/3 / CardName"
    r'\bYuuzhan$'                       # "Yuuzhan Vong" wrapped across lines
    r')',
    re.IGNORECASE
)
currentSet = pd.DataFrame(columns=['Name','Set','ImageFile','Side','Type','Subtype','Cost','Speed','Power','Health','Rarity','Number','Usage','Text','Script','Classification','DraftRarity'])
currentSet.head()

cardSet = "YV"

cwd = os.getcwd()


def _italic_line_indices(layer):
    """Return a set of 0-based line indices where every character is italic.

    Uses the PSD text engine's StyleRun data to check FauxItalic per character,
    then maps character positions back to \\r-delimited lines. Used to detect
    flavor text lines on subordinate cards (which use a single \\r before flavor
    text rather than the double \\r\\r used on standard cards).
    """
    try:
        style_run = layer.engine_dict.get('StyleRun', {})
        runs = style_run.get('RunArray', [])
        lengths = style_run.get('RunLengthArray', [])
        if not runs or not lengths:
            return set()
        # Build a per-character italic map
        italic = []
        for run, length in zip(runs, lengths):
            style = run.get('StyleSheet', {}).get('StyleSheetData', {})
            italic.extend([bool(style.get('FauxItalic', False))] * length)
        # Map character positions to line indices
        text = layer.text
        italic_lines = set()
        pos = 0
        for i, line in enumerate(text.split('\r')):
            end = pos + len(line)
            chars = italic[pos:end]
            # Mark line italic if non-empty and every character is italic
            if line.strip() and chars and all(chars):
                italic_lines.add(i)
            pos = end + 1  # +1 for the \r
        return italic_lines
    except Exception:
        return set()


def processGameText(layer, is_subordinate=False):
    """Extract game text from a PSD layer, inserting | between ability clauses.

    Each \\r in PSD text is an intentional line break between abilities. We
    insert | for new clauses and a plain space for continuation lines (e.g.
    "Play only when...", "If you do,", "Or:" inside a Choose-one ability).

    Fully-italic lines are skipped only on subordinate cards: their flavor text
    follows a single \\r (not the double \\r\\r used on standard cards) and is set
    in italics. Standard cards use \\r\\r to delimit flavor text, so italic
    detection is not applied (reminder text, which is also italic, must be kept).
    """
    try:
        text = layer.text
        # Strip flavor text separated by double \r (standard cards)
        fp = text.find("\r\r")
        if fp != -1:
            text = text[:fp]
        # Normalize special characters (mirrors cleanGameText, preserving \r for splitting)
        # Strip control characters (0x00-0x1F) except \r (0x0D), which is used for line splitting
        text = re.sub(r'[\x00-\x0c\x0e-\x1f]', '', text)
        text = (text.replace("\u00bd", "[Tap]")
                    .replace("<", "[Pilot]")
                    .replace(">", "*")
                    .replace("§", "->")
                    .replace("\u201c", '"')
                    .replace("\u201d", '"')
                    .replace("\u2018", "'")
                    .replace("\u2019", "'"))
        # Identify italic lines (flavor text on subordinate cards only)
        italic_lines = _italic_line_indices(layer) if is_subordinate else set()
        # Split on line breaks and decide: new clause (|) or continuation (space)
        segments = text.split("\r")
        parts = []
        for i, seg in enumerate(segments):
            seg = seg.strip()
            if not seg or i in italic_lines:
                continue
            if not parts:
                parts.append(seg)
            elif (seg[0].islower()
                  or (seg[0] in ('+', '-') and len(seg) > 1 and seg[1].isdigit())
                  or _CONTINUATION_STARTERS.match(seg)
                  or _CONTINUATION_ENDERS.search(parts[-1])):
                # Continuation: append to the current clause with a space
                parts[-1] += " " + seg
            else:
                # New clause
                parts.append(seg)
        return " | ".join(parts)
    except Exception:
        return "[game text]"


def processUniqueLetter(layer):
    """Extract unique letter from a visible layer."""
    if layer.is_visible():
        return layer.text.upper()
    return None


def processBuildCost(layer):
    """Extract build cost from a Build Cost layer group."""
    for child in layer:
        if child.is_visible() and child.name in VALID_BUILD_COSTS:
            return child.text
    return None

def processGenericPSD(psd, imageFrag, fileNameNumber, currentSet):
    card = Card()
    card.imageFrag = imageFrag
    uniqueLetter = None

    if fileNameNumber != "promo" and fileNameNumber != "sub":
        card.number = fileNameNumber

    if fileNameNumber == "promo":
        card.isPromo = True

    if fileNameNumber == "sub":
        card.number = ""

    print("Processing " + fileNameNumber)

    # Temporary storage for name (will be finalized with setCardName at the end)
    rawName = "[name]"

    for layer in psd:
        if layer.name == "Card Text":
            for child in layer:
                if child.name == "Card Name":
                    rawName = child.text
                if child.name == "Unique Letter":
                    letter = processUniqueLetter(child)
                    if letter:
                        uniqueLetter = letter
                if child.name == "Build Cost":
                    cost = processBuildCost(child)
                    if cost:
                        card.buildCost = cost
                if child.name == "Speed":
                    card.speed = child.text
                if child.name == "Power":
                    card.power = child.text
                if child.name == "Health":
                    card.health = child.text
                if child.name == "Typeline":
                    card.setTypeline(child.text)
                # for non-unit the layer is called 'Number'
                if child.name == "Card Number" or child.name == "Number":
                    cardNumberText = child.text
                    card.number = cardNumberText[:cardNumberText.find("/")]
                if "Game Text" in child.name:
                    card.cardText = processGameText(child)

        if layer.name == 'Side Symbols' or layer.name == "Side":
            for child in layer:
                if child.is_visible():
                    card.setSide(child.name)

        if layer.name == 'Rarities':
            for child in layer:
                if child.is_visible():
                    card.setRarity(child.name)

        # Equipment Unique Letters are different
        if layer.name == "Background":
            if layer.is_group():
                for child in layer:
                    if child.is_visible() and child.name == "Equipment":
                        for subChild in child:
                            if subChild.name == "Version Letter":
                                letter = processUniqueLetter(subChild)
                                if letter:
                                    uniqueLetter = letter

        if layer.name == "Card Name":
            rawName = layer.text
        if layer.name == "Unique Letters":
            for child in layer:
                if child.name == "Unique Letter":
                    letter = processUniqueLetter(child)
                    if letter:
                        uniqueLetter = letter
        if layer.name == "Speed":
            card.speed = layer.text
        if layer.name == "Power":
            card.power = layer.text
        if layer.name == "Health":
            card.health = layer.text
        if layer.name == "Subtype (Subordinate)":
            card.setTypeline(layer.text)
        if layer.name == "Game text":
            card.cardText = processGameText(layer, is_subordinate=True)

        # Subordinate side symbols (visible layer at top level)
        if layer.is_visible() and layer.name in ("Light", "Dark", "Neutral", "Yuuzhan Vong"):
            card.setSide(layer.name)

    # Finalize card name with unique letter
    card.setCardName(rawName, uniqueLetter)

    # Validate
    card.validate(imageFrag)
    card.validateNumberMatch(fileNameNumber, imageFrag)
    if uniqueLetter:
        card.validateUniqueLetter(imageFrag)

    # Add to DataFrame
    new_row = card.toSetFileRow(cardSet, classification=cardSet)
    new_row_insert = pd.DataFrame(new_row, index=[0])
    currentSet = pd.concat([new_row_insert, currentSet.loc[:]]).reset_index(drop=True)
    return currentSet


def processPSD(absolutePath, currentSet):
  psd = PSDImage.open(absolutePath)
  fileName = absolutePath[absolutePath.rfind("/") + 1:]
  imageFrag = fileName[:-4]
  if imageFrag[len(cardSet):].startswith("promo"):
    return processGenericPSD(psd, imageFrag, "promo", currentSet)
  elif imageFrag[len(cardSet):].startswith("sub"):
    return processGenericPSD(psd, imageFrag, "sub", currentSet)
  fileNameNumber = ""
  foundStartingDigit = False
  for ch in imageFrag[len(cardSet):]:
    if ch.isdigit():
      if foundStartingDigit or ch != "0":
        fileNameNumber += ch
        foundStartingDigit = True
    else:
      break
  return processGenericPSD(psd, imageFrag, fileNameNumber, currentSet)

#get the file list
filenames = glob.glob(cwd + '/PSDs/*.psd')
for filename in filenames:
  currentSet = processPSD(filename, currentSet)
    
#sort the df
currentSet = currentSet.sort_values('ImageFile')

#output to set txt file
csv_output_path = cwd + "/" + cardSet + ".txt"
currentSet.to_csv(csv_output_path, sep ='\t', index=False, quotechar='%')    
    