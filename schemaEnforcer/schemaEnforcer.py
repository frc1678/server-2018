# Created by Carl Csaposs
# Last Updated: 2/3/18

import pyrebase
import time
import json
from slackclient import SlackClient
import traceback
from collections import OrderedDict

epochTime = time.time()
startTime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epochTime)))

print("")
print("SchemaEnforcer v0.2 by Carl Csaposs")
print("Yells at people who mess up the schema so you don't have to!")
print("")

# schemaEnforcer.py
# Checks firebase against saved data and deletes incorrect data points
# Features:
# - Able to target specific parts of firebase
# - Interface with schemaEnforcer slack bot and yells at people
# - Automatically deletes data (with manual confirmation)
# - Saves deleted data and allows restoring


# LIMITATIONS:
# Does not check for missing data
# Does not check TIMD, tempTIMD, or team child names (does check subchildren)
# Needs correct firebase to compare against
# Feature: ignores AppTokens, because, why not?

# TODO:
# Setup listener

partialCheck = False
keys = ['TempTeamInMatchDatas'] # Ignored unless partialCheck == True

atCompetition = False
bypassCompetitionLimit = False # Doesn't matter if not atCompetition

testMode = False

if testMode:
	print(">>> Testing Mode <<<")
	url = 'servervartest-2018'
else:
	#url = 'servervartest-2018'
	#url = 'scouting-2018-9023a'
	url = 'scouting-2018-temp'
	#url = 'schema-enforcer'

config = {
	"apiKey": "AIzaSyBXfDygtDWxzyRaLFO75XeGc2xhfvLLwkU ",
    "authDomain": url + ".firebaseapp.com",
    "databaseURL": "https://" + url + ".firebaseio.com",
    "projectId": url,
    "storageBucket": url + ".appspot.com",
    "messagingSenderId": "333426669167"

}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

with open('./apikey.txt', 'r') as f:
	apikey = f.read()
slack = SlackClient(apikey)

# Use to find channel id first time (different script please)
'''
channels = slack.api_call('channels.list')
channels = channels['channels']
for channel in range(len(channels)):
	if channels[channel]['name_normalized'] == "2_schema_changes":
		print(channels[channel]['id'])
'''
#channelID = "C8T9MDJ02" # NOT SET


# Run getSchemaFromFirebase.py to update data
with open('./importedData.json', 'rb') as f:
	sD = json.load(f) # sD = saved database

# cF = current firebase
print("Fetching data from firebase...")
if not partialCheck:
	cF = db.child("").get().val()
elif len(keys) == 0:
	print("")
	print(">>>>> No keys in 'keys' list!")
	raise SystemExit(0)
else:
	print(">>> Partial Check <<<")
	cF = {}
	for x in keys:
		cF[x] = db.child(x).get().val()
		if type(cF[x]) == OrderedDict:
			cF[x] = dict(cF[x])
print("Data fetched from firebase.")
print("")

if atCompetition and not bypassCompetitionLimit:
	currentMatch = db.child('currentMatchNum').get().val()
	with open('./matchdata.txt', 'r') as f:
		fileData = f.read()
		if fileData == '':
			with open('./matchdata.txt', 'w') as file:
				file.write(str(currentMatch))
		else:
			if not currentMatch - int(fileData) >= 10:
				print("Current match: " + str(currentMatch))
				print("Last checked: " + fileData)
				print("10 matches have not passed, not checking")
				raise SystemExit(0)
			else:
				with open('./matchdata.txt', 'w') as file:
					file.write(str(currentMatch))
else: # Clear data
	with open('./matchdata.txt', 'w') as f:
		f.write('')

if testMode:
	addon = 'Test'
elif partialCheck:
	addon = 'Partial'
else:
	addon = ''

with open('./backups/liveDatabase'+addon+'-'+startTime+'.json', 'w') as f:
	json.dump(cF, f, indent=4, separators=(',', ':'))

storedSlack = {'key':[], 'type':[], 'list':[]}
deletion = {'key':{}, 'type':{}, 'list':{}}
urls = {'good':'https://i.imgur.com/OKFB8sH.png', 'warning':'https://i.imgur.com/nTGQtC5.png', 'danger':'https://i.imgur.com/uNrneSF.png'}


match0Checked = False

def backupInput():
	x = raw_input("Should backup to restore file? (y/n) ")
	if x == 'y' or x == 'Y':
		doBackup()
		return
	elif x == 'n' or x == 'N':
		return
	else:
		return backupInput()

def doBackup():
	with open('./restores/restore'+startTime+'.json', 'w') as f:
		json.dump(deletion, f, indent=4, separators=(',', ':'))

def deleteInput():
	x = raw_input("Should DELETE and fix? (y/n) ")
	if x == 'y' or x == 'Y':
		y = raw_input("Are you sure? (y/n) ")
		if y == 'y' or y == 'Y':
			return True
		else:
			return deleteInput()
	elif x == 'n' or x == 'n':
		return False
	return deleteInput()

def fixInput():
	x = raw_input("Should try to fix? (y/n) ")
	if x == 'y' or x == 'Y':
		return True
	elif x == 'n' or x == 'N':
		return False
	else:
		return fixInput()

def sendSlack(message, status):
    slack.api_call('chat.postMessage',
        channel = '#2_schema_changes',
        text = message,
        as_user = False,
        username = 'schemaEnforcer',
        icon_url = urls[status],
        #thread_ts =,
        )
def slackTS(message, ts, status):
	slack.api_call('chat.postMessage',
		channel = '#2_schema_changes',
		text = message,
		as_user = False,
		username = 'schemaEnforcer',
		icon_url = urls[status],
		thread_ts = ts)

def storeSlack(message, type):
	storedSlack[type].append(message)

def storeDeletionKey(key, path, type1, value):
	path += "/" + key
	deletion[type1][path] = value

def storeDeletionType(key, path, type1, value, correctType):
	path += "/" + key
	deletion[type1][path] = [value, correctType]

def storeDeletionListType(key, path, type1, value, correctType):
	deletion[type1][path] = [value, correctType]

def shouldSlack():
	if testMode:
		return True # Won't send slack, but allows script to continue
	x = raw_input("Should send slack? (y/n) ")
	if x == 'y' or x == 'Y':
		return True
	elif x == 'n' or x == 'N':
		return False
	else:
		return shouldSlack()

def formatKeyWarning(key, pathList, value):
	path = ""
	for x in pathList:
		path += "/"+str(x)
	storeDeletionKey(str(key), path, 'key', value)
	print("[!] (K) '"+str(key)+"' (P:"+str(path)+") not in stored database!")
	storeSlack("[!] (K) '"+str(key)+"' (P:"+str(path)+") should not exist!", 'key')

def formatTypeWarning(key, typeUsed, typeCorrect, pathList, value):
	if not(typeUsed == int and typeCorrect == float):
		path = ""
		for x in pathList:
			path += "/"+str(x)
		storeDeletionType(str(key), path, 'type', value, str(typeCorrect)[7:-2])
		print("[!] (T) '"+str(key)+"' (P:"+str(path)+") incorrect type: " + str(typeUsed)[7:-2] +", should be type: " +str(typeCorrect)[7:-2])
		storeSlack("[!] (T) '"+str(key)+"' (P:"+str(path)+") incorrect type: " + str(typeUsed)[7:-2] +", should be type: " +str(typeCorrect)[7:-2], 'type')

def formatListTypeWarning(key, numProblems, typeCorrect, pathList):
	path = ""
	for x in pathList:
		path += "/"+str(x)
	storeDeletionListType(str(key), path, 'list', key, str(typeCorrect)[7:-2])
	print("[!] (LT) '"+str(key)+"' (P:"+str(path)+") "+str(numProblems)+" incorrect type(s) in list, all should be: "+str(typeCorrect)[7:-2])
	storeSlack("[!] (LT) '"+str(key)+"' (P:"+str(path)+") "+str(numProblems)+" incorrect type(s) in list, all should be: "+str(typeCorrect)[7:-2], 'list')

def getColorForKey(var):
	if var <= 5:
		return 'good'
	elif var <= 25:
		return 'warning'
	else:
		return 'danger'



try:
	for x in cF:
		if x not in sD:
			formatKeyWarning(x, [], cF[x])
		elif x in ['AppTokens', 'scouts', 'availability', 'availabilityUpdated', 'code']:
			continue # Who cares about app tokens?
		elif x == "TempTeamInMatchDatas" or x == "TeamInMatchDatas" or x == "Teams" or x == "AppTokens":
			if type(cF[x]) == dict and type(sD[x]) == dict:
				for y in cF[x]:
					if y not in sD[x]:
						ry = sD[x].keys()[0]
					else:
						ry = y
					if type(cF[x][y]) == dict and type(sD[x][ry]) == dict:
						for z in cF[x][y]:
							#print('z', z)
							if z == 'imageKeys' or z == 'pitAllImageURLs':
								doNothing = None
							elif z not in sD[x][ry]:
								formatKeyWarning(z, [x,y], cF[x][y][z])
							elif type(cF[x][y][z]) == dict and type(sD[x][ry][z]) == dict:
								for a in cF[x][y][z]:
									if a not in sD[x][ry][z]:
										formatKeyWarning(a, [x,y,z], cF[x][y][z][a])
									elif type(cF[x][y][z][a]) == dict and type(sD[x][ry][z][a]) == dict:
										print('Error 52C: Script needs more continuation')
									elif type(cF[x][y][z][a]) == list and type(sD[x][ry][z][a]) == list:
										for b in sD[x][ry][z][a]:
											if type(b) == dict:
												ix = cF[x][ry][z][a].index(b)
												for c in cF[x][ry][z][a][ix]:
													if c not in sD[x][ry][z][a][ix]:
														formatKeyWarning(c, [x,y,z,a,ix], cF[x][y][z][a][ix][c])
													elif type(c) == dict:
														print("Error 54A: Script needs more continuation")
													elif type(c) == list:
														print("Error 54B: Script needs more continuation")
													else:
														if type(b[c]) != type(sD[x][ry][z][a][ix][c]):
															formatTypeWarning(c, type(b[c]), type(sD[x][ry][z][a][ix][c]), [x,y,z,a,ix], b[c])
											elif type(b) == list:
												print("Error 53H: Script needs more continuation")
											else:
												problemsInList = 0
												for b in cF[x][y][z][a]:
													if type(b) != type(sD[x][ry][z][a][0]):
														problemsInList += 1
												if problemsInList > 0:
													formatListTypeWarning(cF[x][y][z][a], problemsInList, type(sD[x][ry][z][a][0]), [x,y,z,a])


									else:
										if a not in sD[x][ry][z]:
											formatKeyWarning(z, [x,y], cF[x][y][z])
										elif type(cF[x][y][z][a]) != type(sD[x][ry][z][a]):
											formatTypeWarning(a, type(cF[x][y][z][a]), type(sD[x][ry][z][a]), [x,y,z], cF[x][y][z][a])
							elif type(cF[x][y][z]) == list and type(sD[x][ry][z]) == list:
								if type(cF[x][y][z][0]) == dict and type(sD[x][ry][z][0]) == dict:
									for b in cF[x][y][z]:
										'''
										if b not in sD[x][ry][z]:
											h = cF[x][y][z].index(b)
											print('g')
											formatKeyWarning(b, [x,y,z], cF[x][y][z][h])
										'''
										if False:
											print('nope')
										else:
											for c in b:
												h = cF[x][y][z].index(b)
												if c not in sD[x][ry][z][0]:
													formatKeyWarning(c, [x,y,z,h], cF[x][y][z][h][c])
												elif type(b[c]) == dict:
													for d in b[c]:
														if type(b[c][d]) == dict:
															print('Error 52G: Script needs more continuation')
														elif type(b[c][d]) == list:
															print('Error 52F: Script needs more continuation')
														else:
															h = cF[x][y][z].index(b)
															if d not in sD[x][ry][z][0][c]:
																formatKeyWarning(d, [x,y,z,h,c], cF[x][y][z][h][c][d])
															elif type(b[c][d]) != type(sD[x][ry][z][0][c][d]):
																formatTypeWarning(d, type(b[c][d]), type(sD[x][ry][z][0][c][d]), [x,y,z,h,c], cF[x][y][z][h][c][d])
												elif type(b[c]) == list:
													print('Error 52E: Script needs more continuation')
												else:
													h = cF[x][y][z].index(b)
													if c not in sD[x][ry][z][0]:
														formatKeyWarning(c, [x,y,z,h], cF[x][y][z][c])
													elif type(b[c]) != type(sD[x][ry][z][0][c]):
														formatTypeWarning(c, type(b[c]), type(sD[x][ry][z][0][c]), [x,y,z,h], cF[x][y][z][h][c])
								elif type(cF[x][y][z][0]) == list and type(sD[x][ry][z][0]) == list:
									print('Error 52B: Script needs more continuation')
								else:
									problemsInList = 0
									for b in cF[x][y][z]:
										if type(b) != type(sD[x][ry][z][0]):
											problemsInList += 1
									if problemsInList > 0:
										formatListTypeWarning(cF[x][y][z], problemsInList, type(sD[x][ry][z][0]), [x, y, z])
							else:
								if z not in sD[x][ry]:
									formatKeyWarning(z, [x,y], cF[x][y][z])
								elif type(cF[x][y][z]) != type(sD[x][ry][z]):
									formatTypeWarning(z, type(cF[x][y][z]), type(sD[x][ry][z]), [x,y], cF[x][y][z])
					elif type(cF[x][y]) == list and type(sD[x][ry]) == list:
						print("Error 53B: Needs restructuring")
					else:
						if y not in sD[x]:
							formatKeyWarning(y, [x], cF[x][y])
						if type(cF[x][y]) != type(sD[x][ry]):
							formatTypeWarning(y, type(cF[x][y]), type(sD[x][ry]), [x], cF[x][y])
			else:
				if type(cF[x]) != type(sD[x]):
					formatTypeWarning(x, type(cF[x]), type(sD[x]), [], sD[x])
				print("Error 50A: Script needs more continuation")
		elif type(cF[x]) == list and type(sD[x]) == list:		
			if type(cF[x][1]) == dict and type(sD[x][1]) == dict:
				for y in cF[x]: # cF[x] is a list
					if type(y) == list:
						print("Error #1A: Script cannot handle double nested lists")
					elif type(y) == dict:
						for z in y:
							ix = 1#cF[x].index(y)
							aix = cF[x].index(y)
							if aix == 0 and x == 'Matches':
								if (not match0Checked) and cF[x][0] != None:
									formatKeyWarning(aix, [x], cF[x][aix])
									match0Checked = True
							elif z not in sD[x][ix]:
								formatKeyWarning(z, [x,aix], cF[x][aix][z])
							elif type(y[z]) == list:
								if type(y[z][0]) == dict or type(y[z][0]) == list:
									print("Error #1B: Script cannot handle double nested lists")
								else:
									ix = 1#ix = cF[x].index(y)
									if ix == 0 and x == 'Matches':
										if (not match0Checked) and cF[x][0] != None:
											formatKeyWarning(aix, [x], cF[x][aix])
											match0Checked = True
									elif z not in sD[x][ix]:
										formatKeyWarning(z, [x, aix], cF[x][aix][z])
									elif type(y[z]) != type(sD[x][ix][z]):
										formatTypeWarning(y[z], type(y[z]), type(sD[x][ix][z]), [x, aix, z], cF[x][aix][z])
									else:
										# Type check in list
										problemsInList = 0
										for b in y[z]:
											if type(b) != type(sD[x][ix][z][0]):
												problemsInList += 1
										if problemsInList > 0:
											formatListTypeWarning(y[z], problemsInList, type(sD[x][ix][z][0]), [x, aix, z])
							elif type(y[z]) == dict:
								for a in y[z]:
									ix = 1#ix = cF[x].index(y)
									b = y[z][a]
									if a not in sD[x][ix][z]:
										formatKeyWarning(a, [x,aix,z], cF[x][aix][z][a])
									elif type(b) == dict or type(b) == list:
										print("Error #2A: Script needs more continuation")
									else:
										f = ix#cF[x].index(y)
										h = sD[x][f][z]
										if a not in h:
											formatKeyWarning(a, [x,f,z], cF[x][f][z][a])
										elif type(b) != type(h[a]):
											formatTypeWarning(a, type(b), type(h[a]), [x,f,z], cF[x][f][z][a])
							else:
								f = ix#cF[x].index(y)
								h = sD[x][1]
								if z not in h:
									formatKeyWarning(z, [x,f], cF[x][f][z])
								elif type(y[z]) != type(h[z]):
									formatTypeWarning(z, type(y[z]), type(h[z]), [x,f], cF[x][f][z])
					else:
						if y == None and x == "Matches":
							continue
						elif y not in sD[x]:
							formatKeyWarning(y, [x], cF[x][y])
						elif type(y) != type(sD[x][ sD[x].index(y) ]): # y must be in sD[x]
							formatTypeWarning(y, type(y), type(sD[x][ sD[x].index(y) ]), [x], cF[x][y])
			elif type(cF[x][0]) == list and type(sD[x][0]) == list:
				print("Error #4A: Script isn't configured for this")
			else:
				if x not in sD:
					formatKeyWarning(x, [], cF[x])
				elif type(cF[x]) != type(sD[x]):
					formatTypeWarning(x, type(cF[x]), type(sD[x]), [], cF[x])
				else:
					# Type check in list
					problemsInList = 0
					for b in cF[x]:
						if type(b) != type(sD[x][0]):
							problemsInList += 1
					if problemsInList > 0:
						formatListTypeWarning(x, problemsInList, type(sD[x][0]), [])

		elif type(cF[x]) == dict and type(sD[x]) == dict:
			#print(x)
			for y in cF[x]:
				#print(y)
				if y not in sD[x]:
					formatKeyWarning(y, [x], cF[x][y])
				elif type(cF[x][y]) == dict and type(sD[x][y]) == dict:
					for z in cF[x][y]:
						if z not in sD[x][y]:
							formatKeyWarning(z, [x,y], cF[x][y][z])
						elif type(cF[x][y][z]) == dict and type(sD[x][y][z]) == dict:
							for a in cF[x][y][z]:
								if a not in sD[x][y][z]:
									formatKeyWarning(a, [x,y,z], cF[x][y][z][a])
								elif type(cF[x][y][z][a]) == dict and type(sD[x][y][z][a]) == dict:
									print('Error 2C: Script needs more continuation')
								elif type(cF[x][y][z][a]) == list and type(sD[x][y][z][a]) == list:
									print("Error 2D: Script needs more continuation")
								else:
									if a not in sD[x][y][z]:
										formatKeyWarning(z, [x,y], cF[x][y][z])
									elif type(cF[x][y][z][a]) != type(sD[x][y][z][a]):
										formatTypeWarning(z, type(cF[x][y][z][a]), type(sD[x][y][z][a]), [x,y], cF[x][y][z])
						elif type(cF[x][y][z]) == list and type(sD[x][y][z]) == list:
							print("Error 7A: Script needs more continuation")
							''' # Untested code
							if type(cF[x][y][z][0]) == dict and type(sD[x][y][z][0]) == dict:
								#print('dict')
								for b in cF[x][y][z]:
									for c in b:
										if type(b[c]) == dict:
											for d in b[c]:
												if type(b[c][d]) == dict:
													print('Error 2G: Script needs more continuation')
												elif type(b[c][d]) == list:
													print('Error 2F: Script needs more continuation')
												else:
													#print('aignore4', b[c][d])
													print('Error 4A: Script needs more continuation')
										elif type(b[c]) == list:
											print('Error 2E: Script needs more continuation')
										else:
											#print('aignore4', b[c])
											print('Error 4D: Script needs more continuation')
							elif type(cF[x][y][z][0]) == list and type(sD[x][y][z][0]) == list:
								print('Error 2B: Script needs more continuation')
							else:
								#print('aignore3', cF[x][y][z])
								print('Error 4C: Script needs more continuation')
							'''
						else:
							if z not in sD[x][y]:
								formatKeyWarning(z, [x,y], cF[x][y][z])
							elif type(cF[x][y][z]) != type(sD[x][y][z]):
								formatTypeWarning(z, type(cF[x][y][z]), type(sD[x][y][z]), [x,y], cF[x][y][z])
				elif type(cF[x][y]) == list and type(sD[x][y]) == list:
					print("Error 3B: Needs restructuring")
				else:
					if y not in sD[x]:
						formatKeyWarning(y, [x], cF[x][y])
					elif type(cF[x][y]) != type(sD[x][y]):
						formatTypeWarning(y, type(cF[x][y]), type(sD[x][y]), [x], cF[x][y])
		else:
			if x not in sD:
				formatKeyWarning(x, [], cF[x])
			elif type(cF[x]) != type(sD[x]):
				formatTypeWarning(x, type(cF[x]), type(sD[x]), [], cF[x])
except Exception as e:
	#sendSlack("ERROR: "+ str(e), 'danger')
	print("ERROR: " + str(e))
	traceback.print_exc()

numKey = len(storedSlack['key'])
numType = len(storedSlack['type'])
numList = len(storedSlack['list'])
totalConflicts = numKey+numType+numList
areErrors = False
for x in storedSlack:
	if len(storedSlack[x]) > 0:
		areErrors = True

attachmentsText = {}
attachments = []


if areErrors:
	print("")
	keyString = "(K): " + str(numKey) if numKey > 0 else ""
	typeString = "(T): " + str(numType) if numType > 0 else ""
	typeString = ", " + typeString if numKey > 0 and numType > 0 else typeString
	listString =  "(LT): " + str(numList) if numList > 0 else ""
	listString = ", " + listString if (numKey > 0 or numType > 0) and numList > 0 else listString
	pluralFormat = " discrepancies: " if totalConflicts != 1 else " discrepancy: "
	pretext = "Found " +str(totalConflicts)+pluralFormat+keyString+typeString+listString
	if partialCheck:
		pretext = "PARTIAL CHECK: "+pretext
	print('[I] ' + pretext)
	shouldContinue = shouldSlack()
	if shouldContinue:
		if numKey > 25 or numType > 25 or numList > 25:
			status = 'danger'
		elif numKey > 5 or numType > 5 or numList > 5:
			status = 'warning'
		else:
			status = 'good'
		# 'pretext' already set

		if numKey > 0:
			istatus = getColorForKey(numKey)
			attachmentsText['key'] = ""
			for x in storedSlack['key']:
				attachmentsText['key'] += "\n" + x
			attachments.append({
				'color':istatus, 
				'text':attachmentsText['key'], 'title':'Key Errors:',
	        })
	        if numKey > 5:
	        	attachments[len(attachments)-1]['footer'] = 'NOTE: This message can be expanded'


		if numType > 0:
			istatus = getColorForKey(numType)
			attachmentsText['type'] = ""
			for x in storedSlack['type']:
				attachmentsText['type'] += "\n" + x
			attachments.append({
				'color':istatus, 
				'text':attachmentsText['type'], 'title':'Type Errors:',
	        })
	        if numType > 5:
	        	attachments[len(attachments)-1]['footer'] = 'NOTE: This message can be expanded'

		if numList > 0:
			istatus = getColorForKey(numList)
			attachmentsText['list'] = ""
			for x in storedSlack['list']:
				attachmentsText['list'] += "\n" + x
			attachments.append({
				'color':istatus, 
				'text':attachmentsText['list'], 'title':'List Type Errors:',
	        })
	        if numList > 5:
	        	attachments[len(attachments)-1]['footer'] = 'NOTE: This message can be expanded'

		attachments[0]['pretext'] = pretext
		attachments[0]['fallback'] = str(totalConflicts) + ' total discrepancies' if totalConflicts != 1 else str(totalConflicts) + ' total discrepancy'
		attachments[-1]['ts'] = epochTime
		attachments[-1]['footer'] = "schemaEnforcer"
		attachments[-1]['footer_icon'] = urls[status]

		if not testMode:
			slack.api_call('chat.postMessage',
			        channel = '#2_schema_changes',
			        as_user = False,
			        username = 'schemaEnforcer',
			        icon_url = urls[status],
			        attachments = attachments
			)

		shouldDelete = deleteInput()
		print("")
		if shouldDelete:
			doBackup()
			for x in deletion:
				if x == 'key':
					for y in deletion[x]:
						db.child(y).remove()
				elif x == 'type':
					for y in deletion[x]:
						try:
							if deletion[x][y][1] == 'int':
								correct = int(deletion[x][y][0])
							elif deletion[x][y][1] == 'unicode':
								correct = str(deletion[x][y][0])
							elif deletion[x][y][1] == 'float':
								correct = float(deletion[x][y][0])
							else:
								print("[*] Could not fix type at '" +str(y)+"'")
								correct = None
							if correct != None:
								db.child(y).set(correct)
						except:
							print("[*] Could not fix type of '" + str(deletion[x][y][0])+"' (P: "+str(y)+")")
				elif x == 'list':
					for y in deletion[x]:
						print("[*] Cannot fix types in list to '" + deletion[x][y][1] + "' (P:"+str(y)+')')
		else:
			shouldFix = fixInput()
			if shouldFix:
				doBackup()
				for x in deletion:
					if x == 'type':
						for y in deletion[x]:
							try:
								if deletion[x][y][1] == 'int':
									correct = int(deletion[x][y][0])
								elif deletion[x][y][1] == 'unicode':
									correct = str(deletion[x][y][0])
								elif deletion[x][y][1] == 'float':
									correct = float(deletion[x][y][0])
								else:
									print("[*] Could not fix type at '" +str(y)+"'")
									correct = None
								if correct != None:
									db.child(y).set(correct)
							except:
								print("[*] Could not fix type of '" + str(deletion[x][y][0])+"' (P: "+str(y)+")")
					elif x == 'list':
						for y in deletion[x]:
							print("[*] Cannot fix types in list to '" + deletion[x][y][1] + "' (P:"+str(y)+')')

			else:
				backupInput()

	else:
		backupInput()
print("")
print("Done.")
print(startTime)