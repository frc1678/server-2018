# Created by Carl Csaposs
# Last Updated: 2/3/18

import pyrebase
from Tkinter import Tk
from tkFileDialog import askopenfilename
import json

# Fixes incorrect schemaNames at a competition when apps cannot be fixed
# Must run after schemaEnforcer finds data to be fixed

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

def shouldContinue():
	x = raw_input("Type 'y' to continue or 'x' to exit: ")
	if x == 'y' or x == 'Y':
		return True
	elif x == 'x' or x == 'X':
		return False
	else:
		return shouldContinue()

def checkLocation():
	x = raw_input("Use cleaned file? (y/n) ")
	if x == 'y' or x == 'Y':
		return True
	elif x == 'n' or x == 'N':
		return False
	else:
		return checkLocation()

def checkData(string):
	dataGood = True
	for x in range(1,13):
		if string[-(x+1)] == "/":
			finalString = string[-x:]
	try:
		int(finalString)
	except:
		dataGood = False
	return dataGood

def checkType(string, value):
	if type(value) == dict:
		if checkData(string):
			return True
		else:
			return False
	else:
		return True

def shouldDelete():
	x = raw_input("Should delete? (y/n) ")
	if x == 'y' or x == 'Y':
		return True
	elif x == 'n' or x == 'N':
		return False
	else:
		return shouldDelete()

if checkLocation():
	initialDir = './schemaFixer'
else:
	initialDir = '../restores'

# File selector GUI
Tk().withdraw()
filename = askopenfilename(initialdir=initialDir, title='Select a JSON file to fix')



if filename == ():
	print("Canceled.")
	raise SystemExit(0)

with open(filename, 'r') as f:
	data = json.load(f)


with open('./old_data.json', 'w') as f:
	json.dump(data['key'], f, indent=4, separators=(',', ':'))
with open('./fixed_data.json', 'w') as f:
	json.dump(data['key'], f, indent=4, separators=(',', ':'))

print("Open fixed_data.json and make any needed changes.  When done:")

if shouldContinue():
	with open('./fixed_data.json', 'r') as f:
		newData = json.load(f)
	for x in newData:
		if checkType(x, newData[x]):
			db.child(x).set(newData[x])
		else:
			for y in newData[x]:
				string = x+'/'+y
				value = newData[x][y]
				if checkType(string, value):
					db.child(string).set(value)
				else:
					for z in newData[x][y]:
						string = x+'/'+y+'/'+z
						value = newData[x][y][z]
						if checkType(string, value):
							db.child(string).set(value)
						else:
							for a in newData[x][y][z]:
								string = x+'/'+y+'/'+z
								value = newData[x][y][z][a]
								if checkType(string, value):
									db.child(string).set(value)
								else:
									print('[*] Cannot fix ' + x)

	print("")
	with open('./old_data.json', 'r') as f:
		oldData = json.load(f)
	deletion = []
	for x in oldData:
		if x not in newData:
			deletion.append(x)
			print("[!] '"+str(x)+"' will be deleted.")
	if len(deletion) > 0:
		print("Total of "+str(len(deletion))+" object(s) to be deleted.")
		if shouldDelete():
			for x in deletion:
				db.child(x).remove()


	print("Done.")
else:
	print("Canceled.")