import os
import io

baseSetPath = "starwars/sets/"

missingCards = {}
allCards = {}

def constructSetFilePath(setCode):
  basePath = baseSetPath
  return basePath + setCode + ".txt"


def processULCard(imageFrag, currentSet, cards):
	imagePath = baseSetPath + "setimages/" + currentSet + "/" + imageFrag
	if not os.path.exists(imagePath):
		missingCards[imageFrag] = imageFrag + " was missing from folder " + currentSet + ", name taken from updatelist.txt"

	slicedFrag = imageFrag[:-4]
	if slicedFrag not in cards.keys():
		missingCards[slicedFrag] = slicedFrag + " has an updatelist.txt entry but wasn't found in " + currentSet + ".txt"
	else:
		cards[slicedFrag] = False
	


def processSetFile(setCode):
	cards = {}
	with io.open(baseSetPath + setCode + ".txt", "r", encoding='cp1252') as setFile:
		firstLine = True
		for line in setFile:
			if firstLine:
				firstLine = False
				continue
			card = line.split('\t')
			name = card[0]
			imageFrag = card[2]
			cards[imageFrag] = True
			if name in allCards.keys():
				print("Duplicate name found for card: " + name)
			else:
				allCards[name] = True
	return cards


def processUpdateList():
	with io.open("starwars/updatelist.txt", "r", encoding='cp1252') as updateList:
		counter = 0

		# Skip down to the actual cards
		for line in updateList:
			if counter == 0:
				date = line.split('\t')[1]
				if date.endswith('\n'):
					date = date[:-1]
				if len(date) != 8:
					print("Updatelist date format is the wrong number of digits: " + date)
				segments = date.split('-')
				if len(segments) != 3:
					print("Updatelist date has wrong separators: " + date)
				for segment in segments:
					if not segment.isdigit():
						print("Illegal characters in date: " + segment)
			counter += 1
			if not line.startswith("CardImageURLs:"):
				continue
			break


		currentSet = ""
		cards = {}
		for line in updateList:
			nextSet = line.partition('/')[0]
			imageLink = line.split('\t')[0].split('/')[1]
			if nextSet != currentSet:
				for key in cards.keys():
					if cards[key] == True:
						missingCards[key] = key + " from set file " + currentSet + ".txt has no corresponding updatelist.txt entry"
				currentSet = nextSet
				cards = processSetFile(currentSet)
			processULCard(imageLink, currentSet, cards)

def validateOtherDates():
	with io.open("starwars/uninstall.txt", "r", encoding='cp1252') as uninstall:
		line = uninstall.readline()
		while not line.startswith("<dateYYMMDD>"):
			line = uninstall.readline()
		date = line[12:-14]
		if len(date) != 6 or not date.isdigit():
			print("Illegal uninstall.txt date format: " + date)

	with io.open("starwars/version.txt", "r", encoding='cp1252') as version:
		line = version.readline()
		while not line.startswith("<lastupdateYYMMDD>"):
			line = version.readline()
		date = line[18:-20]
		if len(date) != 6 or not date.isdigit():
			print("Illegal version.txt date format: " + date)

	with io.open("starwars/plugininfo.txt", "r", encoding='cp1252') as plugininfo:
		line = plugininfo.readline()
		while not line.startswith("<pluginversion>"):
			line = plugininfo.readline()
		date = line[15:-17]
		if len(date) != 10:
			print("Illegal date format for plugininfo.txt - wrong number of characters: " + date)
		segments = date.split('.')
		if len(segments) != 3:
			print("Illegal separator used in plugininfo.txt: " + date)
		for segment in segments:
			if not segment.isdigit():
				print("Illegal characters used in plugininfo.txt date: " + date)

def main():

  processUpdateList()
  validateOtherDates()
  for key in missingCards:
  	print(missingCards[key])

main()