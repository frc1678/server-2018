import pyrebase
import numpy as np
import utils
import multiprocessing
import firebaseCommunicator
import settingsCommunicator
import time
import pdb
from TBACommunicator import TBACommunicator
import sys
import SPR
import random
import csv

#These are the keys that have lists of dicts
#Lists may have different numbers of dicts, but the keys in the dicts should be the same
listKeys = ['allianceSwitchAttemptAuto', 'allianceSwitchAttemptTele', 'opponentSwitchAttemptTele', 'scaleAttemptAuto', 'scaleAttemptTele']

#For enumerated dicts of platform intakes
boolDictKeys = ['alliancePlatformIntakeAuto', 'alliancePlatformIntakeTele', 'opponentPlatformIntakeTele']

#These ought to be the same across all tempTIMDs for the same TIMD
constants = ['matchNumber', 'teamNumber']

PBC = firebaseCommunicator.PyrebaseCommunicator()
SC = settingsCommunicator.SettingsCommunicator()
firebase = PBC.firebase
tbac = TBACommunicator()
spr = SPR.ScoutPrecision()

class DataChecker(multiprocessing.Process):
	'''Combines data from tempTIMDs into TIMDs...'''
	def __init__(self):
		super(DataChecker, self).__init__()
		self.consolidationGroups = {}

	#Gets a common value for a list depending on the data type
	def commonValue(self, vals, sprKing):
		#If there are several types, they are probably misformatted bools (e.g. 0 or None for False), so attempt tries turning them into bools and trying again
		if len(set(map(type, vals))) != 1:
			return self.attempt(vals, sprKing)
		#If the values are bools, it goes to a function for bools
		elif type(vals[0]) == bool:
			return self.joinBools(vals, sprKing)
		#Text does not need to be joined
		elif type(vals[0]) == str or type(vals[0]) == unicode:
			if vals[0] == 'left' or vals[0] == 'center' or vals[0] == 'right':
				return self.joinStartingPosition(vals, sprKing)
			return vals
		#Otherwise, if the values are something like ints or floats, it goes to a general purpose function
		else:
			return self.joinList(vals, sprKing)

	#Uses commonValue if at least one value is a bool, on the basis that they should all be bools, but some are just not written properly
	def attempt(self, vals, sprKing):
		if map(type, vals).count(bool) > 0:
			return self.commonValue(map(bool, vals), sprKing)

	#Joins the startingPosition data point
	def joinStartingPosition(self, vals, sprKing):
		return 'left' if vals.count('left') > len(vals) / 2 else 'center' if vals.count('center') > len(vals) / 2 else 'right' if vals.count('right') > len(vals) / 2 else vals[sprKing]

	#Gets the most common bool of a list of inputted bools
	def joinBools(self, bools, sprKing):
		return utils.convertNoneToIdentity(utils.mode(bools), bools[sprKing])

	#Takes the didPark data point from TBA if it is available
	def consolidateParking(self, consolidation, matches, key, sprKing):
		team = 'frc' + key.split('Q')[0]
		matchNum = int(key.split('Q')[1])
		match = filter(lambda match: match['match_number'] == matchNum and match['comp_level'] == 'qm', matches)[0]
		try:
			match['score_breakdown']
			allianceColor = 'blue' if team in match['alliances']['blue']['team_keys'] else 'red'
			robotNum = (match['alliances'][allianceColor]['team_keys'].index(team)) + 1
			didPark = (match['score_breakdown'][allianceColor]['endgameRobot' + str(robotNum)] == 'Parking')
		except:
			didPark = self.commonValue(consolidation, sprKing)
		return didPark	

	#Takes the didMakeAutoRun data point from TBA if it is available
	def consolidateAutoRun(self, consolidation, matches, key, sprKing):
		team = 'frc' + key.split('Q')[0]
		matchNum = int(key.split('Q')[1])
		match = filter(lambda match: match['match_number'] == matchNum and match['comp_level'] == 'qm', matches)[0]
		try:
			match['score_breakdown']
			allianceColor = 'blue' if team in match['alliances']['blue']['team_keys'] else 'red'
			robotNum = (match['alliances'][allianceColor]['team_keys'].index(team)) + 1
			didAutoRun = (match['score_breakdown'][allianceColor]['autoRobot' + str(robotNum)] == 'AutoRun')
		except:
			didAutoRun = self.commonValue(consolidation, sprKing)
		return didAutoRun		

	#Returns the most common value in a list, or the average if no value is more than half the list
	def joinList(self, values, sprKing):
		if values:
			a = map(values.count, values)
			mCV = values[a.index(max(a))]
			try:
				return mCV if values.count(mCV) > len(values) / 2 else values[sprKing]
			except:
				try:
					return values[sprKing]
				except:
					return values[-1]

	#Joins a list of booleans
	def commonValueForBoolDict(self, consolidationList, sprKing):
		conjunctionJunction = [[],[],[],[],[],[]]
		for item in consolidationList:
			for number in range(len(item)):
				conjunctionJunction[number].append(item[number])
		dictOfTruth = {}
		for number in range(len(conjunctionJunction)):
			dictOfTruth[number] = self.joinBools(conjunctionJunction[number], sprKing)
		return dictOfTruth

	#Same function as findCommonValuesForKeys except for climbs specifically because of the different schema
	def findCommonValuesForClimb(self, lis, sprKing):
		if lis:
			modeListLength = utils.mode(map(len, lis))
			if modeListLength == None:
				modeListLength = map(len, lis)[sprKing]
			for aScout in lis:
				if len(aScout) < modeListLength:
					aScout += [{'soloClimb' : {'didSucceed': False, 'startTime': 0.0, 'endTime': 0.0}}]
			returnList = []
			for num in range(modeListLength):
				returnList += [{}]
				dicts = [scout[num] for scout in lis]
				consolidationDict = {}
				
				climbTypes = [dic.keys()[0] for dic in dicts]
				if len(climbTypes) == 1:
					climbType = climbTypes[0]
				elif len(climbTypes) % 2 == 0:
					if climbTypes[0] == climbTypes[1]:
						climbType = climbTypes[0]
					else:
						climbType = climbTypes[sprKing]
				else:
					climbFrequencies = map(climbTypes.count, climbTypes)
					commonClimb = climbTypes[climbFrequencies.index(max(climbFrequencies))]
					if max(climbFrequencies) > 1:
						climbType = commonClimb
					else:
						climbType = climbTypes[sprKing]

				offset = 0
				scoutNum = 0
				offsetList = []
				for scout in dicts:
					try:
						scout[climbType]
					except:
						del dicts[dicts.index(scout)]	
						offset += 1
						offsetList + [scoutNum]
					scoutNum += 1
				
				sprKing = sprKing - len([n for n in offsetList if n <= sprKing])
				for key in dicts[0][dicts[0].keys()[0]].keys():
					consolidationDict[key] = []
					for aDict in dicts:
						consolidationDict[key] += [aDict[(aDict.keys()[0])][key]]	
				returnList[num][climbType] = {}
				for key in consolidationDict.keys():
					if key != 'partnerLiftType':
						if sprKing <= (len(consolidationDict[key]) - 1):
							returnList[num][climbType].update({key: self.commonValue(consolidationDict[key], sprKing)})
						else:
							returnList[num][climbType].update({key: self.commonValue(consolidationDict[key], (len(consolidationDict[key]) - 1))})
						
				try:
					if len(consolidationDict['partnerLiftType']) == 1:
						returnList[num][climbType].update({'partnerLiftType': consolidationDict['partnerLiftType'][0]})
					elif len(consolidationDict['partnerLiftType']) % 2 == 0:
						if consolidationDict['partnerLiftType'][0] == consolidationDict['partnerLiftType'][1]:
							returnList[num][climbType].update({'partnerLiftType': consolidationDict['partnerLiftType'][0]})
						else:
							returnList[num][climbType].update({'partnerLiftType': consolidationDict['partnerLiftType'][sprKing]})
							#change to whoever has better SPR
					else:
						liftTypeFrequencies = map(consolidationDict['partnerLiftType'].count, consolidationDict['partnerLiftType'])
						commonLiftType = consolidationDict['partnerLiftType'][liftTypeFrequencies.index(max(liftTypeFrequencies))]
						if max(liftTypeFrequencies) > 1:
							returnList[num][climbType].update({'partnerLiftType': commonLiftType})
						else:
							returnList[num][climbType].update({'partnerLiftType': commonLiftType})
				except:
					pass
			return returnList

	#Joins the vault data point 
	def findCommonValuesForVault(self, lis, sprKing):
		if lis:
			modeListLength = utils.mode(map(len, lis))
			if modeListLength == None:
				modeListLength = map(len, lis)[sprKing]
			for aScout in lis:
				if len(aScout) < modeListLength:
					pass
				elif len(aScout) > modeListLength:
					aScout = aScout[0:modeListLength]
			returnList = []
			for num in range(modeListLength):
				returnList += [{}]
				consolidationDict = {}
				try:
					keys = lis[sprKing][num].keys()
				except:
					keys = ['cubes', 'time']
				for key in keys:
					consolidationDict[key] = []
					for aDict in lis:
						try:
							consolidationDict[key] += [aDict[num][key]]
						except:
							pass
				returnList[num].update({'cubes': self.commonValue(consolidationDict['cubes'], sprKing)})
				times = [time for scout, time in enumerate(consolidationDict['time']) if consolidationDict['cubes'][scout] == returnList[num]['cubes']]
				try:
					stdTimes = utils.stdList(times)
					mean = utils.avg(times)
					zscores = {time : ((time - mean) / stdTimes) for time in times}
					times = [time for time in times if zscores[time] < 1.0]
				except:
					pass
				if times != []:
					returnList[num].update({key: utils.avg(times)})
				else:
					try:
						returnList[num].update({key: consolidationDict['time'][sprKing]})
					except:
						returnList[num].update({key: consolidationDict['time'][(len(consolidationDict['time']) - 1)]})
			return returnList

	#Counts how many cubes a robot placed in the vault from the vault data point
	def totalVaultInput(self, vault):
		totalCubes = 0
		for cycle in vault:
			totalCubes += cycle['cubes']
		return totalCubes

	#Joins lists of dicts
	def findCommonValuesForKeys(self, lis, sprKing):
		if lis:
			modeListLength = utils.mode(map(len, lis))
			if modeListLength == None:
				modeListLength = map(len, lis)[sprKing]
			for aScout in lis:
				if len(aScout) < modeListLength:
					aScout += [{'didSucceed': False, 'startTime': 0.0, 'endTime': 0.0}] * (modeListLength - len(aScout))
				elif len(aScout) > modeListLength:
					aScout = aScout[0:modeListLength]
			returnList = []
			for num in range(modeListLength):
				returnList += [{}] #adds a list of dictionaries to the returnList for every character (the length) in the largest list
				#Finds dicts that should be the same (e.g. status) within the tempTIMDs
				#This means comparisons such as the first cube attempt in teleop by a given robot, as recorded by multiple scouts
				dicts = [scout[num] for scout in lis]
				consolidationDict = {}
				#Combines dicts that should be the same into a consolidation dict-penisandpussy
				for key in ['didSucceed', 'startTime', 'endTime', 'status', 'layer']:
					consolidationDict[key] = []
					for aDict in dicts:
						try:
							consolidationDict[key] += [aDict[key]]
						except:
							if key == 'status':
								consolidationDict[key] += ['owned']
							elif key == 'layer':
								consolidationDict[key] += [1]
					if 'Time' in key:
						consolidationDict[key] = [float(k) for k in consolidationDict[key]]
						returnList[num].update({key: self.commonValue(consolidationDict[key], sprKing)})
				#Same thing with didSucceed
				if len(consolidationDict['didSucceed']) == 1:
					returnList[num].update({'didSucceed': consolidationDict['didSucceed'][0]})
				elif len(consolidationDict['didSucceed']) % 2 == 0:
					returnList[num].update({'didSucceed': consolidationDict['didSucceed'][sprKing]})
					#change to whoever has better SPR
				else:
					successFrequencies = map(consolidationDict['didSucceed'].count, consolidationDict['didSucceed'])
					commonSuccess = consolidationDict['didSucceed'][successFrequencies.index(max(successFrequencies))]
					if max(successFrequencies) > 1:
						returnList[num].update({'didSucceed': commonSuccess})
					else:
						returnList[num].update({'didSucceed': consolidationDict['didSucceed'][sprKing]})
				offset = 0
				offsetList = []
				if False in consolidationDict['didSucceed'] and returnList[num]['didSucceed'] == True:
					for number in range(len(consolidationDict['didSucceed'])):
						if consolidationDict['didSucceed'][(number - offset)] == False:
							for item in consolidationDict:
								del consolidationDict[item][(number - offset)]
							offset += 1
							offsetList + [number]

				sprKing = sprKing - len([n for n in offsetList if n <= sprKing])
				if returnList[num]['didSucceed'] == True:
					#If there is only one scout, their statement about status is accepted as right
					if len(consolidationDict['status']) == 1:
						returnList[num].update({'status': consolidationDict['status'][0]})
					elif len(consolidationDict['status']) % 2 == 0:
						if consolidationDict['status'][0].lower() == consolidationDict['status'][1].lower():
							returnList[num].update({'status': consolidationDict['status'][0]})
						else:
							if sprKing <= (len(consolidationDict['status']) - 1):
								returnList[num].update({'status': consolidationDict['status'][sprKing]})
							else:
								returnList[num].update({'status': consolidationDict['status'][(len(consolidationDict['status']) - 1)]})
							#change to whoever has better SPR
					#If there are 3 scouts (or more, but that shouldn't happen), the status value is the most common status value
					else:
						statusFrequencies = map(consolidationDict['status'].count, consolidationDict['status'])
						commonStatus = consolidationDict['status'][statusFrequencies.index(max(statusFrequencies))]
						if max(statusFrequencies) > 1:
							returnList[num].update({'status': commonStatus})
						else:
							if sprKing <= (len(consolidationDict['status']) - 1):
								returnList[num].update({'status': consolidationDict['status'][sprKing]})
							else:
								returnList[num].update({'status': consolidationDict['status'][(len(consolidationDict['status']) - 1)]})
					#Same thing with layer
					if len(consolidationDict['layer']) == 1:
						returnList[num].update({'layer': consolidationDict['layer'][0]})
					elif len(consolidationDict['layer']) % 2 == 0:
						if consolidationDict['layer'][0] == consolidationDict['layer'][1]:
							returnList[num].update({'layer': consolidationDict['layer'][0]})
						else:
							if sprKing <= (len(consolidationDict['status']) - 1):
								returnList[num].update({'layer': consolidationDict['layer'][sprKing]})
							else:
								returnList[num].update({'layer': consolidationDict['layer'][(len(consolidationDict['status']) - 1)]})
							#change to whoever has better SPR
					else:
						layerFrequencies = map(consolidationDict['layer'].count, consolidationDict['layer'])
						commonLayer = consolidationDict['layer'][layerFrequencies.index(max(layerFrequencies))]
						if max(layerFrequencies) > 1:
							returnList[num].update({'layer': commonLayer})
						else:
							if sprKing <= (len(consolidationDict['status']) - 1):
								returnList[num].update({'layer': consolidationDict['layer'][sprKing]})
							else:
								returnList[num].update({'layer': consolidationDict['layer'][(len(consolidationDict['status']) - 1)]})
			return returnList

	#Combines data from whole TIMDs
	def joinValues(self, key, matches, sprDict):
		returnDict = {}
		sprKing = self.getSPRKing(sprDict, map(lambda tm: (tm.get('scoutName') or []), self.consolidationGroups[key]))
		#Flattens the list of lists of keys into a list of keys
		for k in self.getAllKeys(map(lambda v: v.keys(), self.consolidationGroups[key])):
			if k in boolDictKeys:
				#Finds a common value for a dictionary of bools
				returnDict.update({k: self.commonValueForBoolDict(self.getConsolidationList(key, k), sprKing)})
			elif k in listKeys:
				#Gets a common value for lists of dicts (for cube values) and puts it into the combined TIMD
				returnDict.update({k: self.findCommonValuesForKeys(map(lambda tm: (tm.get(k) or []), self.consolidationGroups[key]), sprKing)})
			elif k == 'didPark':
				#Gets didPark from TBA
				returnDict.update({k: self.consolidateParking(self.getConsolidationList(key, k), matches, key, sprKing)})
			elif k == 'didAutoRun':
				#Gets didAutoRun from TBA
				returnDict.update({k: self.consolidateAutoRun(self.getConsolidationList(key, k), matches, key, sprKing)})
			elif k == 'climb':
				#Finds a common value for climbs 
				returnDict.update({k: self.findCommonValuesForClimb(map(lambda tm: (tm.get(k) or []), self.consolidationGroups[key]), sprKing)})
			elif k == 'vault':
				#Gets a common value for lists of dicts (for cube values) and puts it into the combined TIMD
				returnDict.update({k: self.findCommonValuesForVault(map(lambda tm: (tm.get(k) or []), self.consolidationGroups[key]), sprKing)})
			elif k == 'mode' or k == 'cycle':
				pass
			elif k in constants:
				#Constants should be the same across all tempTIMDs, so the common value is just the value in one of them
				#Puts the value into the combined TIMD
				returnDict.update({k: self.consolidationGroups[key][0][k]})
			else:
				#Gets a common value across any kind of list of values and puts it into the combined TIMD
				returnDict.update({k: self.commonValue(self.getConsolidationList(key, k), sprKing)})
		try:
			returnDict.update({'numExchangeInput' : self.totalVaultInput(returnDict['vault'])})
		except:
			returnDict.update({'numExchangeInput' : 0})
		return returnDict

	#Gets the index of the scout with the lowest SPR
	def getSPRKing(self, sprDict, scoutNames):
		try:
			sortedList = sorted(scoutNames, key = lambda scout: sprDict[scout])
			if sortedList:
				return scoutNames.index(sortedList[0])
			else:
				return 0
		except:
			return 0

	#Creates a dictionary of all of the scouts' sprs
	def getSPRList(self):
		sprs = SC.firebase.child('SPRs').get().val()
		return dict(sprs)

	#Flattens the list of lists of keys into a list of keys
	def getAllKeys(self, keyArrays):
		return list(set([v for l in keyArrays for v in l]))

	#Gets common values for values in each of a list of dicts
	def avgDict(self, dicts):
		keys = self.getAllKeys(map(lambda d: d.keys(), dicts))
		return {k : self.commonValue(map(lambda v: (v.get(k) or 0), dicts)) for k in keys}

	def getConsolidationList(self, key, k):
		listToConsolidate = []
		for tm in self.consolidationGroups[key]:
			if tm.get(k) != None:
				listToConsolidate += [tm.get(k)]
			else:
				listToConsolidate += [0]
		return listToConsolidate

	#Gathers tempTIMDs for the current match
	def getConsolidationGroups(self, tempTIMDs, curMatch):
		actualKeys = list(set([key.split('-')[0] for key in tempTIMDs.keys()]))
		return {key : [v for k, v in tempTIMDs.items() if k.split('-')[0] == key] for key in actualKeys if int(key.split('Q')[1]) > (int(curMatch) - 5)}

	#Gathers all of the tempTIMDs for a full cycle
	def getFullConsolidationGroups(self, tempTIMDs, curMatch):
		actualKeys = list(set([key.split('-')[0] for key in tempTIMDs.keys()]))
		return {key : [v for k, v in tempTIMDs.items() if k.split('-')[0] == key] for key in actualKeys}

	#Retrieves and consolidates tempTIMDs from firebase and combines their data, putting the result back onto firebase as TIMDs
	def run(self, isFull):
		tempTIMDs = firebase.child('TempTeamInMatchDatas').get().val()
		#Keeps on iterating over the tempTIMDs until none exists on firebase
		if tempTIMDs == None:
			time.sleep(5)
			print('> No tempTIMDs to compute\n')
			return
		print('> TempTIMDs taken from firebase...')
		matches = tbac.makeEventMatchesRequest()
		curMatch = firebase.child('currentMatchNum').get().val()
		if isFull:
			self.consolidationGroups = self.getFullConsolidationGroups(tempTIMDs, curMatch)
		else:
			self.consolidationGroups = self.getConsolidationGroups(tempTIMDs, curMatch)
		index = 0
		sprDict = self.getSPRList()
		while index < len(self.consolidationGroups.keys()):
			key = sorted(self.consolidationGroups.keys(), key = lambda k: int(k.split('Q')[1]), reverse = True)[index]
			print('> Consolidating ' + key)
			#Updates a TIMD on firebases
			try:
				firebase.child('TeamInMatchDatas').child(key).update(self.joinValues(key, matches, sprDict))
				index += 1
			except Exception as e:
				print(e)
