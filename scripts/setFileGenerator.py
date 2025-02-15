from psd_tools import PSDImage
import pandas as pd
import os
import glob

validBuildCosts = ['Multi-arena build', 'Space build', 'Ground build', 'Character build', 'Space Build', 'Ground Build', 'Character Build', 'Resource Build', 'Trap Build', 'Campaign Build', 'Mission Build', 'Trait Build', 'Skill Build', 'Equipment Build', 'Multi-Arena Build', 'Resource Build']
currentSet = pd.DataFrame(columns=['Name','Set','ImageFile','Side','Type','Subtype','Cost','Speed','Power','Health','Rarity','Number','Usage','Text','Script','Classification'])
currentSet.head()            

cardSet = "VDR"

cwd = os.getcwd()

class Card:
  cardName = "[name]"
  buildCost = "[buildCost]"
  speed = "[speed]"
  power = "[power]"
  health = "[health]"
  typeline = "[typeline]"
  cardNumber = ""
  cardText = "[game text]"
  side = "[side]"
  rarity = "[rarity]"
  uniqueLetter = ""
  isUnit = False
  sideCount = 0
  rarityCount = 0


def logIssue(cardName, field, reason):
  print(cardName + " -- issue proccessing field: " + field + " -- " + reason)


def processGameText(layer):
  try:
    cardText = layer.text
    flavor_position = cardText.find("\r\r")
    if flavor_position != -1:
      cardText = cardText[:flavor_position]
    cardText = cardText.replace("\r"," ").replace("§","->").replace('<', '').replace('“','"').replace('”','"').replace('’', "'").replace("½", "Tap")
    return cardText
  except:
    return "[game text]" 

def processCardName(layer):
  cardName = layer.text.replace('’', "'")
  return cardName

def processUniqueLetter(layer, letter):
  if layer.is_visible():
    letter = layer.text.upper()
  return letter

def processSubordinateSides(layer, side, sideCount):
    if layer.name == "Dark":
        if layer.is_visible():
            side = "D"
            sideCount += 1
    if layer.name == "Light":
        if layer.is_visible():
            side = "L"
            sideCount += 1
    if layer.name == "Neutral":
        if layer.is_visible():
            side = "N"
            sideCount += 1
    if layer.name == "Yuuzhan Vong":
        if layer.is_visible():
            side = "Y"
            sideCount += 1
    return side, sideCount

def processBuildCost(layer):
  for child in layer:
    if child.is_visible() and child.name in validBuildCosts:
      return child.text

def processGenericPSD(psd, imageFrag, fileNameNumber, currentSet):
    card = Card()

    if fileNameNumber != "promo" and fileNameNumber != "sub":
      card.cardNumber = fileNameNumber

    print("Processing " + fileNameNumber)

    for layer in psd:
        if layer.name == "Card Text":
            for child in layer:
                if child.name == "Card Name":
                    card.cardName = processCardName(child)
                if child.name == "Unique Letter":
                    card.uniqueLetter = processUniqueLetter(child, card.uniqueLetter)
                if child.name == "Build Cost":
                    card.buildCost = processBuildCost(child)
                if child.name == "Speed":
                    card.speed = child.text
                if child.name == "Power":
                    card.power = child.text
                if child.name == "Health":
                    card.health = child.text
                if child.name == "Typeline":
                        card.typeline = child.text.lstrip(" ")
                        if card.typeline.lower().startswith("space") or card.typeline.lower().startswith("ground") or card.typeline.lower().startswith("character"):
                          card.isUnit = True
                # for non-unit the layer is called 'Number'
                if child.name == "Card Number" or child.name == "Number":
                        cardNumbertext = child.text
                        card.cardNumber = cardNumbertext[:cardNumbertext.find("/")]
                
                if ("Game Text") in child.name:
                        card.cardText = processGameText(child)
            
                        
            if card.typeline.lower().startswith("event") or card.typeline.lower().startswith("battle"):
              card.buildCost = ""
            elif card.buildCost == "[buildCost]":
              logIssue(imageFrag, buildCost, " no correctly named layer found")
            if card.typeline == "[typeline]":
              logIssue(imageFrag, typeline, " no correctly named layer found")
            if card.isUnit:
              if card.speed == "[speed]":
                logIssue(imageFrag, card.speed, " no correctly named layer found")
              if card.power == "[power]":
                logIssue(imageFrag, card.power, " no correctly named layer found")
              if card.health == "[health]":
                logIssue(imageFrag, card.health, " no correctly named layer found")
            else:
              card.speed = ""
              card.power = ""
              card.health = ""
            if card.cardNumber == "[number]":
              logIssue(imageFrag, "[number]",  " no correctly named layer found")
            elif fileNameNumber != "promo" and card.cardNumber != fileNameNumber:
              logIssue(imageFrag, "[number]", " number on card (" + card.cardNumber + ") doesn't match number in file name (" + fileNameNumber + ")")
            if card.cardText == "[game text]":
              logIssue(imageFrag, card.cardText,  " no correctly named layer found")
            

        if layer.name == 'Side Symbols' or layer.name == "Side":
            for child in layer:
               if child.is_visible():
                   match child.name:
                       case "Light":
                           card.side = "L"
                           card.sideCount += 1
                       case "Neutral":
                           card.side = "N"
                           card.sideCount += 1
                       case "Dark":
                           card.side = "D"
                           card.sideCount += 1
                       case "Yuuzhan Vong":
                           card.side = "Y"
                           card.sideCount += 1
            if card.sideCount == 0 or card.sideCount > 1:
              logIssue(imageFrag, "[side]", str(card.sideCount) + " layers marked visible")
              card.side = "[side]"
                      
        if layer.name == 'Rarities':
            for child in layer:
              if child.is_visible():
                match child.name:
                  case "Common":
                    card.rarity = 'C'
                    card.rarityCount += 1
                  case "Uncommon":
                    card.rarity = 'U'
                    card.rarityCount += 1
                  case "Rare":
                    card.rarity = 'R'
                    card.rarityCount += 1
                  case "Promo":
                    card.rarity = 'P'
                    card.rarityCount += 1

          #Equipment Unique Letters are different
        if layer.name == "Background":
          if layer.is_group():
            for child in layer:
              if child.is_visible():
                if child.name == "Equipment":
                  for subChild in child:
                    if subChild.name == "Version Letter":
                      card.uniqueLetter = processUniqueLetter(subChild, card.uniqueLetter)

        if layer.name == "Card Name":
            card.cardName = processCardName(layer)
        if layer.name == "Unique Letters":
            for child in layer:
              match child.name:
                case "Unique Letter":
                  card.uniqueLetter = processUniqueLetter(child, card.uniqueLetter)
        if layer.name == "Speed":
            card.speed = layer.text
        if layer.name == "Power":
            card.power = layer.text
        if layer.name == "Health":
            card.health = layer.text
        if layer.name == "Subtype (Subordinate)":
            card.typeline = layer.text
        if layer.name == "Game text":
            card.cardText = processGameText(layer)
        card.side, card.sideCount = processSubordinateSides(layer, card.side, card.sideCount)


    dash_position = card.typeline.find("-")
    card.typeline  = card.typeline.lower()
    if card.typeline.startswith("mission") or card.typeline.startswith("battle") or card.typeline.startswith("event") or card.typeline.startswith("resource"):
        cardType = card.typeline.lstrip(" ").title().rstrip()
        subtype = ""
    else:
        if dash_position != -1:
          cardType = card.typeline[0:dash_position]
          cardSubtype = card.typeline[dash_position + 1:]
          cardType = cardType.lstrip(" ").title().rstrip()
          subtype = cardSubtype.lstrip(" ").title().replace("\r"," ").rstrip()
        else:
          cardType = card.typeline
          subtype = "" 
    
    if card.typeline.lstrip(" ").startswith("subordinate"):
        card.buildCost = ""
        card.rarity = "S"


    # Validate
    if len(card.uniqueLetter) > 0:
      card.cardName = card.cardName.rstrip('\n')
      card.cardName = card.cardName.rstrip('\r')
      card.cardName = card.cardName.rstrip('\r\n')
      card.cardName = card.cardName + " (" + card.uniqueLetter + ")"
      if card.uniqueLetter != imageFrag[-len(card.uniqueLetter):]:
        logIssue(imageFrag, "uniqueLetter", " unique letter in card (" + card.uniqueLetter + ") doesn't match unique letter in file name (" + imageFrag[-len(card.uniqueLetter):] + ")")
        print(imageFrag)
    if card.typeline == "[typeline]":
      logIssue(imageFrag, card.typeline,  " no correctly named layer found")
    if card.speed == "[speed]":
      logIssue(imageFrag, card.speed,  " no correctly named layer found")
    if card.power == "[power]":
      logIssue(imageFrag, card.power,  " no correctly named layer found")
    if card.health == "[health]":
      logIssue(imageFrag, card.health,  " no correctly named layer found")
    if card.cardText == "[game text]":
      logIssue(imageFrag, card.cardText,  " no correctly named layer found")
    if card.sideCount == 0 or card.sideCount > 1:
      logIssue(imageFrag, "[side]", str(card.sideCount) + " layers marked visible")
      card.side = "[side]"
    if card.rarityCount > 1 or (card.rarityCount == 0 and card.rarity != "S") :
      logIssue(imageFrag, "[rarity]", str(card.rarityCount) + " layers maked visible")
      card.rarity = "[rarity]"


    card.cardName = card.cardName.rstrip()
    new_row = {'Name':card.cardName,'Set':cardSet,'ImageFile':imageFrag,'Side':card.side,'Type':cardType,'Subtype':subtype,
           'Cost':card.buildCost,'Speed':card.speed,'Power':card.power,'Health':card.health,'Rarity':card.rarity,'Number':card.cardNumber,
           'Usage':'','Text':card.cardText,'Script':'','Classification':''}
    new_row_insert = pd.DataFrame(new_row, index=[0])
    currentSet = pd.concat([new_row_insert,currentSet.loc[:]]).reset_index(drop=True)
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
    