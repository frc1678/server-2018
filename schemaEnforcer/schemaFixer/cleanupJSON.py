import json
from Tkinter import Tk
from tkFileDialog import askopenfilename

# Removes information from a restore JSON file
# If there's too many discrepancies or only a certain one should be targeted,
# makes it easier to use schemaFixer.py


# If true, will remove items in keyList from export
# If false, will remove all items except those in keyList
removeMode = True 

keyList = ['/TempTeamInMatchDatas/1Q1-18/teamNumber',]

# File selector GUI
Tk().withdraw() 
filename = askopenfilename(initialdir = '../restores', title = 'Select JSON file to clean')

if filename == ():
	print("Canceled.")
else:
	with open(filename, 'r') as f:
		data = json.load(f)

	firstRun = True
	output = {'key':{}}
	for x in data['key']:
		if (x in keyList) == (False if removeMode else True):
			if firstRun == True:
				output['key'] = {}
				firstRun = False
			output['key'][x] = data['key'][x]

	with open('./cleaned.json', 'w') as f:
		json.dump(output, f, indent=4, separators=(',', ':'))

	print("Done.")
