#Last Updated: 2/7/18
import pyrebase
import numpy as np
import utils
import multiprocessing
import firebaseCommunicator
import time
import pdb
from TBACommunicator import TBACommunicator
import sys
import SPR
import random

#These are the keys that have lists of dicts
#Lists may have different numbers of dicts, but the keys in the dicts should be the same
listKeys = ['allianceSwitchAttemptAuto', 'allianceSwitchAttemptTele', 'opponentSwitchAttemptTele', 'scaleAttemptAuto', 'scaleAttemptTele']

#For enumerated dicts of platform intakes
boolDictKeys = ['alliancePlatformIntakeAuto', 'alliancePlatformIntakeTele', 'opponentPlatformIntakeTele']

#These ought to be the same across all tempTIMDs for the same TIMD
constants = ['matchNumber', 'teamNumber']

PBC = firebaseCommunicator.PyrebaseCommunicator()
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

	def joinStartingPosition(self, vals, sprKing):
		return 'left' if vals.count('left') > len(vals) / 2 else 'center' if vals.count('center') > len(vals) / 2 else 'right' if vals.count('right') > len(vals) / 2 else vals[sprKing]

	#Gets the most common bool of a list of inputted bools
	def joinBools(self, bools, sprKing):
		return False if bools.count(False) > len(bools) / 2 else bools[sprKing]

	#Returns the most common value in a list, or the average if no value is more than half the list
	def joinList(self, values, sprKing):
		if values:
			a = map(values.count, values)
			mCV = values[a.index(max(a))]
			try:
				return mCV if values.count(mCV) > len(values) / 2 else values[sprKing]
			except:
				return

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
			largestListLength = max(map(len, lis))
			for aScout in lis:
				if len(aScout) < largestListLength:
					aScout += [{'soloClimb' : {'didSucceed': False, 'startTime': 0.0, 'endTime': 0.0}}]
			returnList = []
			for num in range(largestListLength):
				returnList += [{}]
				dicts = [scout[num] for scout in lis]
				consolidationDict = {}
				for key in dicts[0][dicts[0].keys()[0]].keys():
					consolidationDict[key] = []
					for aDict in dicts:
						consolidationDict[key] += [aDict[(aDict.keys()[0])][key]]
				#Finds the correct climbType for the climb		
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
				returnList[num][climbType] = {}
				for key in consolidationDict.keys():
					if key != 'partnerLiftType':
						returnList[num][climbType].update({key: self.commonValue(consolidationDict[key], sprKing)})
				#Strange happenings in the down-low - Don't ask if you can't handle the truth
				try:
					if len(consolidationDict['partnerLiftType']) == 1:
						returnList[num][climbType].update({'partnerLiftType': consolidationDict['partnerLiftType']})
					elif len(consolidationDict['partnerLiftType']) % 2 == 0:
						if consolidationDict['partnerLiftType'][0] == consolidationDict['partnerLiftType'][1]:
							returnList[num][climbType].update({'partnerLiftType': consolidationDict['partnerLiftType'][0]})
						else:
							returnList[num][climbType].update({'partnerLiftType': consolidationDict['partnerLiftType'][random.randint(0, 1)]})
							#change to whoever has better SPR
					else:
						#Do nOt sPEaK iF YoU ChOOse NoT tO FoLLOw - Sc.Ar.l
						liftTypeFrequencies = map(consolidationDict['partnerLiftType'].count, consolidationDict['partnerLiftType'])
						commonLiftType = consolidationDict['partnerLiftType'][liftTypeFrequencies.index(max(liftTypeFrequencies))]
						if max(liftTypeFrequencies) > 1:
							returnList[num][climbType].update({'partnerLiftType': commonLiftType})
						else:
							returnList[num][climbType].update({'partnerLiftType': commonLiftType})
				except:
					pass
			return returnList

	def findCommonValuesForKeys(self, lis, sprKing):
		if lis:
			largestListLength = max(map(len, lis))
			for aScout in lis:
				if len(aScout) < largestListLength:
					aScout += [{'didSucceed': False, 'startTime': 0.0, 'endTime': 0.0, 'status': 'balanced', 'layer': 0}] * (largestListLength - len(aScout))
			returnList = []
			for num in range(largestListLength):
				returnList += [{}] #adds a list of dictionaries to the returnList for every character (the length) in the largest list
				#Finds dicts that should be the same (e.g. status) within the tempTIMDs
				#This means comparisons such as the first cube attempt in teleop by a given robot, as recorded by multiple scouts
				dicts = [scout[num] for scout in lis]
				consolidationDict = {}
				#Combines dicts that should be the same into a consolidation dict-penisandpussy
				for key in dicts[0].keys():
					consolidationDict[key] = []
					for aDict in dicts:
						consolidationDict[key] += [aDict[key]]
					if 'Time' in key:
						returnList[num].update({key: self.commonValue(consolidationDict[key], sprKing)})
				#If there is only one scout, their statement about status is accepted as right
				if len(consolidationDict['status']) == 1:
					returnList[num].update({'status': consolidationDict['status'][0]})
				elif len(consolidationDict['status']) % 2 == 0:
					if consolidationDict['status'][0].lower() == consolidationDict['status'][1]:
						returnList[num].update({'status': consolidationDict['status'][0]})
					else:
						returnList[num].update({'status': consolidationDict['status'][sprKing]})
						#change to whoever has better SPR
				#If there are 3 scouts (or more, but that shouldn't happen), the status value is the most common status value
				else:
					statusFrequencies = map(consolidationDict['status'].count, consolidationDict['status'])
					commonStatus = consolidationDict['status'][statusFrequencies.index(max(statusFrequencies))]
					if max(statusFrequencies) > 1:
						returnList[num].update({'status': commonStatus})
					else:
						returnList[num].update({'status': consolidationDict['status'][sprKing]})
				#Same thing with layer
				if len(consolidationDict['layer']) == 1:
					returnList[num].update({'layer': consolidationDict['layer'][0]})
				elif len(consolidationDict['layer']) % 2 == 0:
					if consolidationDict['layer'][0] == consolidationDict['layer'][1]:
						returnList[num].update({'layer': consolidationDict['layer'][0]})
					else:
						returnList[num].update({'layer': consolidationDict['layer'][sprKing]})
						#change to whoever has better SPR
				else:
					layerFrequencies = map(consolidationDict['layer'].count, consolidationDict['layer'])
					commonLayer = consolidationDict['layer'][layerFrequencies.index(max(layerFrequencies))]
					if max(layerFrequencies) > 1:
						returnList[num].update({'layer': commonLayer})
					else:
						returnList[num].update({'layer': consolidationDict['layer'][sprKing]})
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
			return returnList

	#Combines data from whole TIMDs
	def joinValues(self, key):
		returnDict = {}
		sprKing = self.getSPRKing(map(lambda tm: (tm.get('scoutName') or []), self.consolidationGroups[key]))
		#Flattens the list of lists of keys into a list of keys
		for k in self.getAllKeys(map(lambda v: v.keys(), self.consolidationGroups[key])):
			if k in boolDictKeys:
				#Finds a common value for a dictionary of bools
				returnDict.update({k: self.commonValueForBoolDict(self.getConsolidationList(key, k), sprKing)})
			elif k in listKeys:
				#Gets a common value for lists of dicts (for cube values) and puts it into the combined TIMD
				returnDict.update({k: self.findCommonValuesForKeys(map(lambda tm: (tm.get(k) or []), self.consolidationGroups[key]), sprKing)})
			elif k == 'climb':
				#Finds a common value for climbs 
				returnDict.update({k: self.findCommonValuesForClimb(map(lambda tm: (tm.get(k) or []), self.consolidationGroups[key]), sprKing)})
			elif k in constants:
				#Constants should be the same across all tempTIMDs, so the common value is just the value in one of them
				#Puts the value into the combined TIMD
				returnDict.update({k: self.consolidationGroups[key][0][k]})
			else:
				#Gets a common value across any kind of list of values and puts it into the combined TIMD
				returnDict.update({k: self.commonValue(self.getConsolidationList(key, k), sprKing)})
		return returnDict

	#Gets the index of the scout with the lowest SPR
	def getSPRKing(self, scoutNames):
		if scoutNames:
			if spr.sprs:
				return 0 if spr.sprs[scoutNames[0]] == min([spr.sprs[scoutName] for scoutName in scoutNames]) else 1 if spr.sprs[scoutNames[1]] == min([spr.sprs[scoutName] for scoutName in scoutNames]) else 2 if spr.sprs[scoutNames[0]] == min([spr.sprs[scoutName] for scoutName in scoutNames]) else random.randint(0,3) 
			else:
				return 0
		else:
			return 0

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

	#Consolidates tempTIMDs for the same team and match
	def getConsolidationGroups(self, tempTIMDs):
		actualKeys = list(set([key.split('-')[0] for key in tempTIMDs.keys()]))
		return {key : [v for k, v in tempTIMDs.items() if k.split('-')[0] == key] for key in actualKeys}

	#Retrieves and consolidates tempTIMDs from firebase and combines their data, putting the result back onto firebase as TIMDs
	def run(self):
		spr.sprs = {'' : 1.5, 'k': 0.5}
		while(True):
			tempTIMDs = firebase.child('TempTeamInMatchDatas').get().val()
			#Keeps on iterating over the tempTIMDs until none exists on firebase
			if tempTIMDs == None:
				time.sleep(5)
				continue
			self.consolidationGroups = self.getConsolidationGroups(tempTIMDs)
			index = 0
			while index < len(self.consolidationGroups.keys()):
				key = self.consolidationGroups.keys()[index]
				#Updates a TIMD on firebase
				try:
					firebase.child('TeamInMatchDatas').child(key).update(self.joinValues(key))
					index += 1
				except Exception as e:
					continue
			time.sleep(10)

DataChecker().start()