from psd_tools import PSDImage
import pandas as pd
import os
import glob

from SWTCG import Card, cleanGameText, VALID_BUILD_COSTS
currentSet = pd.DataFrame(columns=['Name','Set','ImageFile','Side','Type','Subtype','Cost','Speed','Power','Health','Rarity','Number','Usage','Text','Script','Classification'])
currentSet.head()

cardSet = "LEG"

cwd = os.getcwd()


def processGameText(layer):
    """Extract and clean game text from a PSD layer."""
    try:
        return cleanGameText(layer.text)
    except:
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
            card.cardText = processGameText(layer)

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
    