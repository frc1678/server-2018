#Last Updated: 1/4/18
import DataModel
import json
import time
import math
import numpy as np
import pdb
import firebaseCommunicator
from collections import Counter

########## Defining Util/Convenience Functions ############
'''If there were too many more of these, or if this
were actual server code, I would make a module, but
for fake database creation purposes it is not worth it'''

def stdList(lis):
	return np.std(lis)

def mode(lis):
	highestItemCount = [0, 0]
	for item, count in dict(Counter(lis)).items():
		if count > highestItemCount[1]:
			highestItemCount = [item, count]
		elif count == highestItemCount[1]:
			highestItemCount += [item, count]
	return highestItemCount[0] if len(highestItemCount) <= 2 else None

def nullifyOutwardValue(v):
	return v if v > 0 and v < 135 else 0 if v < 135 else 135

def matrixZscores(m):
	mean = np.mean(m)
	std = np.std(m)
	for rowNum, row in enumerate(range(m.shape[0])):
		for columnNum, column in enumerate(range(m.shape[1])):
			m[rowNum][columnNum] = float((m[rowNum][columnNum] - mean)) / std
	return m

def avg(lis):
	l = [False if x == None else x for x in lis]
	return float(sum(l)) / len(l)

def removeNoneFrom(lis):
	return [x for x in lis if x != None]

def replaceFromNone(lis, replace):
	return [replace if x == None else x for x in lis]

def sumStdDevs(stdDevs):
	return sum(map(lambda x: x ** 2 , filter(lambda s: s != None, stdDevs))) ** 0.5

def convertFirebaseBoolean(fbBool):
	if type(fbBool) in [int, bool]: return bool(fbBool)
	return True if fbBool == 'true' else False

def rms(values):
	if len(values) == 0: return
	return math.sqrt(np.mean(map(lambda x: x ** 2, values)))

def convertNoneToIdentity(x, identity):
	return identity if x == None else x

def convertIdentity(x, identity, testvar):
	return identity if x == testvar else x

def dictOperation(dict1, dict2, dictOp, identity):
	newDict = {}
	map(lambda k: setDictionaryValue(newDict, k, dictOp(convertNoneToIdentity(dict1[k], identity), convertNoneToIdentity(dict2[k], identity))), dict1)
	return newDict

def dictSum(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: x + y, 0)

def dictDifference(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: x - y, 0)

def dictProduct(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: x * y, 1)

def dictQuotient(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: float(x) / float(y) if float(y) != 0.0 else None, 1.0)

def dictPercentage(dict1, dict2):
	return dictQuotient(dict1, dictSum(dict1, dict2))

def dictDivideConstant(d, constant):
	returnDict = {}
	[setDictionaryValue(returnDict, k, (float(v) / constant)) for k, v in d.iteritems()]
	return returnDict

def stdDictSum(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: sumStdDevs([x, y]))

def setDictionaryValue(dict, key, value):
	dict[key] = value

def makeMatchFromDict(d):
	match = DataModel.Match(**d)
	if 'calculatedData' in d.keys():
		match.calculatedData = DataModel.CalculatedMatchData(**d['calculatedData'])
	return match

def makeTeamFromDict(d):
	if type(d) != dict: print(d)
	team = DataModel.Team(**d)
	if 'calculatedData' in d.keys():
		team.calculatedData = DataModel.CalculatedTeamData(**d['calculatedData'])
	return team

def makeTIMDFromDict(d):
	timd = DataModel.TeamInMatchData(**d)
	if 'calculatedData' in d.keys():
		timd.calculatedData = DataModel.CalculatedTeamInMatchData(**d['calculatedData'])
	return timd

def makeTeamsFromDicts(dicts):
	return map(makeTeamFromDict, dicts.values())

def makeMatchesFromDicts(dicts):
	try:
		return [makeMatchFromDict(dicts[m]) for m in dicts if m != None]
	except:
		return [makeMatchFromDict(m) for m in dicts if m != None]

def makeDictFromObject(o):
	if isinstance(o, dict):
		[setDictionaryValue(o, k, v) for k, v in o.iteritems() if v.__class__ in [DataModel.CalculatedTeamData, DataModel.CalculatedMatchData, DataModel.CalculatedTeamInMatchData]]
		return o
	return dict((key, value) for key, value in o.__dict__.iteritems() if not callable(value) and not key.startswith('__'))

def readValueFromObjectDict(objectDict, key):
	return objectDict[key]

def makeDictFromTeam(t):
	d = makeDictFromObject(t)
	d['calculatedData'] = makeDictFromObject(d['calculatedData'])
	return d

def makeDictFromMatch(t):
	d = makeDictFromObject(t)
	d['calculatedData'] = makeDictFromObject(d['calculatedData'])
	return d

def makeDictFromTIMD(timd):
	d = makeDictFromObject(timd)
	d['calculatedData'] = makeDictFromObject(d['calculatedData'])
	return d

def makeDictFromCalculatedData(calculatedData):
	return calculatedData.__dict__

def makeTIMDsFromDicts(timds):
	return [makeTIMDFromDict(timd) for timd in timds.values() if timd != None]

def makeTeamObjectWithNumberAndName(number, name):
	team = Team()
	team.name, team.number = name, number
	return team

def makeTIMDFromTeamNumberAndMatchNumber(teamNumber, matchNumber):
	timd = DataModel.TeamInMatchData()
	timd.teamNumber, timd.matchNumber = teamNumber, matchNumber
	return timd

def setDataForMatch(match):
	m = DataModel.Match()
	m.number, m.redAllianceTeamNumbers, m.blueAllianceTeamNumbers = int(match['match_number']), match['alliances']['red']['team_keys'], match['alliances']['blue']['team_keys']
	return m

def setDataForTeam(team):
	t = DataModel.Team()
	t.number, t.name, t.teamInMatchDatas = team['team_number'], team['nickname'], []
	return t

def printWarningForSeconds(numSeconds):
	print(str(numSeconds) + ' SECONDS UNTIL FIREBASE WIPES')
	time.sleep(1)

def extendList(lis):
	#Turns a list of lists into one big list
	return [v for l in lis for v in l]

def extendListWithStrings(lis):
	returnList = []
	for l in lis:
		if type(l) == list:
			for v in l:
				returnList += v
		else:
			returnList += l
	return returnList

def sum_to_n(n, limit = None):
	#Finds possible groupings of individuals (n of them) into a specified number of groups (size) with each group's maximum size of limit
	#e.g. sum_to_n(6, 3) -> (2,2,2), (1,2,3)
	#sum_to_n(6, 3, 3) -> (2,2,2)
    combos = []
    good = []
    if limit is None:
        limit = n
    for x in range(1, limit):
    	for y in range(1, limit):
    		for z in range(1, limit):
    			for x1 in range(1, limit):
    				for y2 in range(1, limit):
    					for z3 in range(1, limit):
    						combos.append([x,y,z,x1,y2,z3])
    for lis in combos:
    	if sum(lis) == n:
    		good.append(lis)
    return good

def makeASCIIFromJSON(input):
    if isinstance(input, dict):
        return dict((makeASCIIFromJSON(k), makeASCIIFromJSON(v)) for k, v in input.items())
    elif isinstance(input, list):
        return map(lambda i: makeASCIIFromJSON(i), input)
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
