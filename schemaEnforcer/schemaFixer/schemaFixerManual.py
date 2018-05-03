# Created by Carl Csaposs
# Last Updated: 2/3/18

import pyrebase
import json
import sys

if not (sys.version_info > (3,0)):
	print("[!] This script requires Python 3!")
	raise SystemExit(0)

# REQUIRES PYTHON 3
# Automates schemaFixer for certain paths

url = 'removedurl'

config = {
	"apiKey": "apikey",
    "authDomain": url + ".firebaseapp.com",
    "databaseURL": "https://" + url + ".firebaseio.com",
    "projectId": url,
    "storageBucket": url + ".appspot.com",
    "messagingSenderId": "333426669167"

}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# * = wildcard
fixList = [ # Set 2nd item in list to '' (empty string) to delete data instead of move
	['/Matches/*/blueAllianceTeamNumbers/calculatedData/blueCubesForPowerup', '/Matches/*/blueCubesForPowerup'],
	['/Matches/*/calculatedData/test/blueScore', '/Matches/*/blueScore'],
]

print("schemaFixerManual by Carl Csaposs...")

def checkForWildcard(string):
	children = []
	lastSlash = 0
	path = []
	for characterIndex in range(1, len(string)): # Removes first slash
		character = string[characterIndex]
		if characterIndex == len(string)-1:
			children.append(string[lastSlash+1:characterIndex+1])
		elif character == '/':
			children.append(string[lastSlash+1:characterIndex])
			lastSlash = characterIndex
	if children.count("*") > 1:
		print("[!] Error: Only 1 wildcard per path allowed")
		raise SystemExit(0)
	elif "*" in children:
		return [True, children]
	else:
		return [False, children]


for item in fixList:
	hasWildcard = []
	resultPath = []
	for string in item:
		result = checkForWildcard(string)
		resultPath.append(result[1])
		if result[0]:
			hasWildcard.append(True)
		else:
			hasWildcard.append(False)
	if True in hasWildcard:
		if hasWildcard[0] == True and hasWildcard[1] == True:
			paths = []
			for singleResult in resultPath:
				for child in singleResult:
					if child == '*':
						firstPartKey = ""
						secondPartKey = ""
						for x in range(len(singleResult)):
							if x < singleResult.index("*"):
								firstPartKey += singleResult[x]+"/"
							elif x > singleResult.index("*"):
								secondPartKey += singleResult[x]+"/"
				if resultPath.index(singleResult) == 0:
					paths.append([firstPartKey, secondPartKey])
				else:
					paths.append([firstPartKey, secondPartKey])
			wildcardChildren = list(db.child(paths[0][0]).shallow().get().val())
			for child in wildcardChildren:
				data = db.child(paths[0][0]+str(child)+'/'+paths[0][1]).get().val()
				if data != None:
					if item[1] != '':
						db.child(paths[1][0]+str(child)+'/'+paths[1][1]).set(data)
					db.child(paths[0][0]+str(child)+'/'+paths[0][1]).remove()

		else:
			print('[!] Error: Wildcard must be used in both items in nested list or not at all.')
	else:
		data = db.child(item[0]).get().val()
		if data != None:
			if item[1] != '':
				db.child(item[1]).set(data)
			db.child(item[0]).remove()

print("Done.")