import os
import io

basePluginPath = "starwars/"
baseSetPath = basePluginPath + "sets/"

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
	with io.open(constructSetFilePath(setCode), "r", encoding='cp1252') as setFile:
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
	with io.open(basePluginPath + "updatelist.txt", "r", encoding='cp1252') as updateList:
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

def main():

  processUpdateList()
  validateOtherDates()
  for key in missingCards:
  	print(missingCards[key])

main()