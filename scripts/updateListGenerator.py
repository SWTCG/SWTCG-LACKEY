import os
import io


setCode = "VDR"


basePluginPath = "../starwars"
baseSetPath = basePluginPath + "sets/"


def constructSetFilePath(setCode):
  basePath = baseSetPath
  return basePath + setCode + ".txt"


def processUpdateList():
	with io.open(basePluginPath + "updatelist.txt", "a", encoding='cp1252') as updateList:

		with io.open(constructSetFilePath(setCode), "r", encoding='utf-8') as setFile:
			firstLine = True
			for line in setFile:
				if firstLine:
					firstLine = False
					continue
				card = line.split('\t')
				name = card[0]
				imageFrag = card[2]
				rarity = card[10]
				number = card[11]
				if number == "":
					if rarity == "S":
						number = "sub"
					elif rarity == "P":
						number = "promo"
				newLine = setCode + "/" + imageFrag + ".jpg" + "	" + "https://lackey.swtcg.com/starwars/sets/setimages/" + setCode + "/" + imageFrag + ".jpg\n"
				updateList.write(newLine)
			setFile.close()
			updateList.close()


def main():
  processUpdateList()

main()