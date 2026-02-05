import io
from SWTCG import getCardFromLine


setCode = "LEG"


basePluginPath = "../starwars"
baseSetPath = basePluginPath + "/sets/"


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
				try:
					card = getCardFromLine(line)
				except (IndexError, KeyError):
					continue
				if not card:
					continue
				newLine = setCode + "/" + card.imageFrag + ".jpg" + "	" + "https://lackey.swtcg.com/starwars/sets/setimages/" + setCode + "/" + card.imageFrag + ".jpg\n"
				updateList.write(newLine)
			setFile.close()
			updateList.close()


def main():
  processUpdateList()

main()