#Last Updated: 2/9/18
import utils
import Math
import random
import numpy as np
import scipy.stats as stats
import CSVExporter
import pprint
import firebaseCommunicator
import json

pbc = firebaseCommunicator.PyrebaseCommunicator()

#Scout Performance Analysis
class ScoutPrecision(object):
	'''Scores and ranks scouts and assigns them to robots'''
	def __init__(self):
		super(ScoutPrecision, self).__init__()
		self.sprs = {}
		self.numTablets = 18
		self.robotNumToScouts = []
		#These keys are the names of sections of the tempTIMDs on which scouts will be graded
		#The value is the weight, since some data points are more important than others
		self.gradingKeys = {
			'didGetDisabled': 2.0,
			'didGetIncapacitated': 2.0,
			'didMakeAutoRun': 2.0,
			'didPark': 3.0,
			'numCubesFumbledAuto': 1.0,
			'numCubesFumbledTele': 1.0,
			'numElevatedPyramidIntakeAuto': 1.0,
			'numElevatedPyramidIntakeTele': 1.0,
			'numExchangeInput': 1.5,
			'numGroundIntakeTele': 1.0,
			'numGroundPortalIntakeTele': 1.0,
			'numGroundPyramidIntakeAuto': 1.0,
			'numGroundPyramidIntakeTele': 1.0,
			'numHumanPortalIntakeTele': 1.0,
			'numReturnIntake': 1.0,
			'numSpilledCubesAuto': 1.0,
			'numSpilledCubesTele': 1.0,
			'startingPosition': 0.5,
		}
		self.gradingLists = {
			'alliancePlatformIntakeAuto': 1.0,
			'alliancePlatformIntakeTele': 1.0,
			'opponentPlatformIntakeTele': 1.0,
		}
		self.gradingDicts = { # Not used 2018
		}
		self.gradingListsOfDicts = { # First value in list is weight for incorrect length
			'allianceSwitchAttemptAuto': [2.5, {
				'didSucceed': 2.0,
				'layer': 2.0,
				'startTime': 0.0,
				'endTime': 0.0,
				'status': 2.0,
			}],
			'allianceSwitchAttemptTele': [2.5, {
				'didSucceed': 2.0,
				'layer': 2.0,
				'startTime': 0.0,
				'endTime': 0.0,
				'status': 2.0,
			}],
			'opponentSwitchAttemptTele': [2.5, {
				'didSucceed': 2.0,
				'layer': 2.0,
				'startTime': 0.0,
				'endTime': 0.0,
				'status': 2.0,
			}],
			'scaleAttemptAuto': [2.5, {
				'didSucceed': 2.0,
				'layer': 2.0,
				'startTime': 0.0,
				'endTime': 0.0,
				'status': 2.0,
			}],
			'scaleAttemptTele': [2.5, {
				'didSucceed': 2.0,
				'layer': 2.0,
				'startTime': 0.0,
				'endTime': 0.0,
				'status': 2.0,
			}]
		}
		self.gradingListsOfDictsDicts = {
			
			'climb': [3.0, 2.5, {
				'assistedClimb':{
					'didSucceed': 1.5,
					'startTime': 0.0,
					'endTime': 0.0,
				},
				'activeLift':{
					'didSucceed': 1.5,
					'didClimb': 1.5,
					'startTime': 0.0,
					'endTime': 0.0,
					'partnerLiftType': 1.5,
					'didFailToLift': 1.5,
					'numRobotsLifted': 1.5,
				},
				'passiveClimb':{
					'didSucceed': 1.5,
					'startTime': 0.0,
					'endTime': 0.0,
				},
				'soloClimb':{
					'didSucceed': 1.5,
					'startTime': 0.0,
					'endTime': 0.0,
				}
			}]
		}

		self.SPRBreakdown = {}
		self.disagreementBreakdown = {}
		self.scoutNumMatches = {}
		self.unusedTablets = []
		self.avgScore = 1

	#SPR
	#Scout precision rank(ing): checks accuracy of scouts by comparing their past TIMDs to the consensus
	#Outputs list of TIMDs that an inputted scout was involved in
	def getTotalTIMDsForScoutName(self, scoutName, tempTIMDs):
		if tempTIMDs:
			return len(filter(lambda v: v.get('scoutName') == scoutName, tempTIMDs.values()))
		else:
			return 0

	#Finds keys that start the same way and groups their values into lists under the keys
	#Used to combine tempTIMDs for the same match by different scouts
	def consolidateTIMDs(self, temp):
		consolidationGroups = {}
		for k, v in temp.items():
			key = k.split('-')[0]
			if key in consolidationGroups.keys():
				consolidationGroups[key].append(v)
			else:
				consolidationGroups[key] = [v]
		return {k : v for k, v in consolidationGroups.items() if len(v) > 1}

	#Note: the next 3 functions compare data in tempTIMDs to find scout accuracy
	#The comparison to determine correct values is done in dataChecker

	#Compares scout performances for individual data points in tempTIMDs
	def findOddScoutForDataPoint(self, tempTIMDs, key):
		weight = self.gradingKeys[key]
		#Finds scout names in tempTIMDs
		scouts = filter(lambda v: v != None, map(lambda k: k.get('scoutName'), tempTIMDs))
		#Finds values (at an inputted key) in tempTIMDs
		values = filter(lambda v: v != None, map(lambda t: t[key] if t.get('scoutName') else None, tempTIMDs))
		#Finds the most common value in the list of values, or the average if none of them is the majority
		if values:
			mode = utils.mode(values)
			#If less than half of the values agree, SPR should not be affected
			if values.count(mode) >= (len(values) / 2) and mode != None:
				#Makes a list of the differences from the common value multiplied by weight, for relative importance of data points
				differenceFromMode = [weight if x != mode else 0 for x in values]
				#Adds the difference from this tempTIMD for this key to each scout's previous differences (spr score)
				for c in range(len(differenceFromMode)):
					self.SPRBreakdown.update({key: (self.SPRBreakdown.get(key) or []) + [(differenceFromMode[c])]})
					#Updates disagreements by category and scout
					if differenceFromMode[c] != 0:
						self.disagreementBreakdown[scouts[c]].update({key: (self.disagreementBreakdown[scouts[c]].get(key) or 0) + 1})
						self.sprs.update({scouts[c] : (self.sprs.get(scouts[c]) or 0) + differenceFromMode[c]})

	def findOddScoutForList(self, tempTIMDs, key):
		weight = self.gradingLists[key]
		scouts = filter(lambda v: v != None, map(lambda k: k.get('scoutName'), tempTIMDs))
		lists = filter(lambda v: v != None, map(lambda t: t[key] if t.get('scoutName') else None, tempTIMDs))
		# Checks to make sure all the lists are the same length (2018 specific)
    # (A set can not have repeat values, so if a set is len of 1, they are all the same length)
		if len(set([len(lis) for lis in lists])) == 1:
			for index in range(len(lists[0])):
				items = [lists[x][index] for x in range(len(lists))]
				mode = utils.mode(items)
				differenceFromMode = [weight if x != mode else 0 for x in items]
				for c in range(len(differenceFromMode)):
					if differenceFromMode[c] != 0:
						self.disagreementBreakdown[scouts[c]].update({key: self.disagreementBreakdown[scouts[c]].get(key, 0) + 1})
						self.sprs.update({scouts[c]: (self.sprs.get(scouts[c]) or 0) + differenceFromMode[c]})

	def findOddScoutForDict(self, tempTIMDs, key):
		# Not used 2018, needs changes to weight items in a dict differently if used

		#Similar to findOddScoutForDataPoint, but for each data point inside of a dict
		weight = self.gradingDicts[key]
		scouts = filter(lambda v: v, map(lambda k: k.get('scoutName'), tempTIMDs))
		dicts = filter(lambda k: k, map(lambda t: t[key] if t.get('scoutName') else None, tempTIMDs))
		#if dicts != None:
		# Needs updated code to use

	def findOddScoutForListOfDicts(self, tempTIMDs, key1):
		#Similar to findOddScoutForDict, but for lists of dicts instead of individual dicts
		#The nth dict on each list should be the same
		weight = self.gradingListsOfDicts[key1][0]
		allScouts = filter(lambda v: v, map(lambda k: k.get('scoutName'), tempTIMDs))
		# Unsorted meaning they can have different lengths
		unsortedLists = filter(lambda k: k, map(lambda t: t.get(key1) if t.get('scoutName') else None, tempTIMDs))
		#Finds the mode for length of dicts and ignores if not that length
		#i.e. if there is disagreement over how many shots a robot took
		if unsortedLists != None:
			modeListLength = utils.mode([len(lis) for lis in unsortedLists]) # finds mode, not max
			modeAmount = [len(lis) for lis in unsortedLists].count(modeListLength)
			#If someone missed an attempt or had an extra attempt, there is no way to compare their data
			#This filters out anything with a different length of dicts
			# 2018 - each dict is an attempt
			lists = []
			aScouts = []
			for aScoutIndex in range(len(unsortedLists)):
				if len(unsortedLists[aScoutIndex]) == modeListLength:
					lists.append(unsortedLists[aScoutIndex])
					aScouts.append(allScouts[aScoutIndex])
				elif modeAmount > 1: # Updates SPR if incorecct list amount and at least 2 scouts agree
					self.sprs.update({allScouts[aScoutIndex]: (self.sprs.get(allScouts[aScoutIndex]) or 0) + weight})
					self.disagreementBreakdown[allScouts[aScoutIndex]].update({key1:{'amount': (self.disagreementBreakdown[allScouts[aScoutIndex]].get(key1, {}).get('amount', 0) + 1) }})
			# Need at least 2 scouts to compare, or SPR is not affected
			if modeAmount > 1:
				# check here with if statement before runing code below
				for num in range(modeListLength):
					#Comparing dicts that should be the same (e.g. each shot time dict for the same shot) within the tempTIMDs
					#This means the nth shot by a given robot in a given match, as recorded by multiple scouts
					#The comparison itself is the same as the other findOddScout functions
					dicts = [lis[num] for lis in lists]
					scouts = [scout for scout in aScouts]

					values = []
					for aDict in dicts:
						values += [aDict['didSucceed']]
					modeSuccess = utils.mode(values)
					if modeSuccess != None:
						popList = []
						weight = self.gradingListsOfDicts[key1][1]['didSucceed']
						for aDictIndex in range(len(dicts)):
							if dicts[aDictIndex]['didSucceed'] != modeSuccess:
								popList.append(aDictIndex)
						for item in popList[::-1]:
							#self.SPRBreakdown.update({key2: (self.SPRBreakdown.get(key2) or []) + [(differenceFromMode[c])]})
							self.sprs.update({scouts[item] : (self.sprs.get(scouts[item]) or 0) + weight})
							self.disagreementBreakdown[scouts[item]].update({key1:{'didSucceed': (self.disagreementBreakdown[scouts[item]].get(key1, {}).get('didSucceed', 0) + 1) }})
							dicts.pop(item)
							scouts.pop(item)
						for key2 in dicts[0].keys():
							#Strings can be averaged (we're just looking at mode, not subtracting them)
							#Without averaging, one person could be declared correct for no reason
							values = [aDict[key2] for aDict in dicts]
							weight = self.gradingListsOfDicts[key1][1][key2]
							mode = utils.mode(values)
							if mode != None:
								differenceFromMode = [weight if v != mode else 0 for v in values]
								#Gets inaccuracy by category
								for c in range(len(differenceFromMode)):
									self.SPRBreakdown.update({key2: (self.SPRBreakdown.get(key2) or []) + [(differenceFromMode[c])]})
									if weight != 0.0:
										self.sprs.update({scouts[c] : (self.sprs.get(scouts[c]) or 0) + differenceFromMode[c]})
										self.disagreementBreakdown[scouts[c]].update({key1:{key2: (self.disagreementBreakdown[scouts[c]].get(key1, {}).get(key2, 0) + 1) }})

	def findOddScoutForListOfDictsDicts(self, tempTIMDs, key1):
		# Similar to findOddScoutForListOfDicts, but for a (dict in dict) in a list
		#The nth dict on each list should be the same
		weight = self.gradingListsOfDictsDicts[key1][0]
		allScouts = filter(lambda v: v, map(lambda k: k.get('scoutName'), tempTIMDs))
		# Unsorted meaning they can have different lengths
		unsortedLists = [tempTIMDs[tempTIMD].get(key1, []) for tempTIMD in range(len(tempTIMDs)) if tempTIMDs[tempTIMD].get('scoutName')]
		#Finds the mode for length of dicts and ignores if not that length
		#i.e. if there is disagreement over how many shots a robot took
		if unsortedLists:
			lenList = [len(lis) for lis in unsortedLists]
			modeListLength = utils.mode(lenList)
			modeAmount = lenList.count(modeListLength)
			#If someone missed an attempt or had an extra attempt, there is no way to compare their data
			#This filters out anything with a different length of dicts
			# 2018 - each dict is an attempt
			# This is year specific code for 2018!
			lists = []
			scouts = []
			for aScoutIndex in range(len(unsortedLists)):
				if len(unsortedLists[aScoutIndex]) == modeListLength:
					lists.append(unsortedLists[aScoutIndex])
					scouts.append(allScouts[aScoutIndex])
				elif modeAmount > 1: # Updates SPR if incorecct list amount and at least 2 scouts agree
					self.sprs.update({allScouts[aScoutIndex]: (self.sprs.get(allScouts[aScoutIndex]) or 0) + weight})
					self.disagreementBreakdown[allScouts[aScoutIndex]].update({key1:{'amount': (self.disagreementBreakdown[allScouts[aScoutIndex]].get(key1, {}).get('amount', 0) + 1) }})
			# Need at least 2 scouts to compare, or SPR is not affected
			if modeAmount > 1:
				for num in range(modeListLength):
					#Comparing dicts that should be the same (e.g. each shot time dict for the same shot) within the tempTIMDs
					#This means the nth shot by a given robot in a given match, as recorded by multiple scouts
					#The comparison itself is the same as the other findOddScout functions
					dicts = [lis[num] for lis in lists]
					keys = []
					for x in dicts:
						keys.append(x.keys()[0])
					modeKey = max(set(keys), key=keys.count)
					modeKeyAmount = keys.count(modeKey)

					dicts2 = []
					scouts2 = []
					weight = self.gradingListsOfDictsDicts[key1][1]
					for index in range(len(dicts)):
						if dicts[index].keys()[0] == modeKey:
							dicts2.append(dicts[index])
							scouts2.append(scouts[index])
						else:
							self.sprs.update({scouts[index]: (self.sprs.get(scouts[index]) or 0) + weight})
							self.disagreementBreakdown[scouts[index]].update({key1:{'climbType': (self.disagreementBreakdown[scouts[index]].get(key1, {}).get('climbType', 0) + 1) }})
					# Must have 2 scouts to compare, or SPR is not affected
					if modeKeyAmount > 1: 
						for key2 in dicts2[0].keys():
							for key3 in dicts2[0][key2].keys():
								#Strings can be averaged (we're just looking at mean, not subtracting them)
								#Without averaging, one person could be declared correct for no reason
								values = []
								for aDict in dicts2:
									values += [aDict[key2][key3]]
								
								weight = self.gradingListsOfDictsDicts[key1][2][key2][key3]
								if weight != 0.0:
									mode = utils.mode(values)
									if mode:	
										differenceFromMode = map(lambda v: weight if v != mode else 0, values)
										#Gets inaccuracy by category
										for c in range(len(differenceFromMode)):
											self.SPRBreakdown.update({key2: (self.SPRBreakdown.get(key2) or []) + [(differenceFromMode[c])]})
											self.sprs.update({scouts2[c] : (self.sprs.get(scouts2[c]) or 0) + differenceFromMode[c]})
											self.disagreementBreakdown[scouts2[c]].update({key1:{key2:{key3: (self.disagreementBreakdown[scouts2[c]].get(key1, {}).get(key2, {}).get(key3, 0) + 1) }}})

	def calculateScoutPrecisionScores(self, temp, available):
		if temp:
			#Combines all tempTIMDs for the same match
			g = self.consolidateTIMDs(temp)
			#Makes a list of scouts with data
			priorScouts = [ind['scoutName'] for timd in g.values() for ind in timd]
			priorScouts = set(priorScouts) #updates priorScouts so that one scoutName cannot appear more than once
			for scout in priorScouts:
				self.disagreementBreakdown.update({scout: {}})
			#Removes any data from previous calculations from sprs
			self.sprs = {}
			'''These grade each scout for each of the values in the grading items
			Each scout gets more 'points' for each incorrect datapoint
			The grades are stored by scout name in sprs
			See the findOddScout functions for details on how'''
			[self.findOddScoutForDataPoint(v, k) for v in g.values() for k in self.gradingKeys.keys()]
			[self.findOddScoutForList(v, k) for v in g.values() for k in self.gradingLists.keys()]
			#Not used 2018 #[self.findOddScoutForDict(v, k) for v in g.values() for k in self.gradingDicts.keys()] # Not used 2018, needs changes
			[self.findOddScoutForListOfDicts(v, k) for v in g.values() for k in self.gradingListsOfDicts.keys()]
			[self.findOddScoutForListOfDictsDicts(v, k) for v in g.values() for k in self.gradingListsOfDictsDicts.keys()]
			'''Divides values for scouts by number of TIMDs the scout has participated in
			If a scout is in more matches, they will likely have more disagreements, but the same number per match if they are equally accurate
			If someone has no tempTIMDs (but still an SPR key somehow), their SPR score is set to -1 (changed in the next section)'''
			self.sprs = {k:((v / float(self.getTotalTIMDsForScoutName(k, temp))) if self.getTotalTIMDsForScoutName(k, temp) > 0 else -1) for (k, v) in self.sprs.items()}
			#Makes an average number of disagreements per scout per category
			avgScout = {}
			for scout in self.disagreementBreakdown.keys():
				for key in self.disagreementBreakdown[scout].keys():
					if type(self.disagreementBreakdown[scout][key]) == dict:
						for item in self.disagreementBreakdown[scout][key]:
							if type(self.disagreementBreakdown[scout][key][item]) == dict:
								for item2 in self.disagreementBreakdown[scout][key][item]:
									try:
										self.disagreementBreakdown[scout].update({key: {item: {item2: float(self.disagreementBreakdown[scout][key][item][item2]/float(self.getTotalTIMDsForScoutName(scout, temp)))}}})
									except:
										pass
							else:
								try:
									self.disagreementBreakdown[scout].update({key: {item: float(self.disagreementBreakdown[scout][key][item]/float(self.getTotalTIMDsForScoutName(scout, temp)))}})
								except:
									pass
					else:
						try:
							self.disagreementBreakdown[scout].update({key: float(self.disagreementBreakdown[scout][key]) / float(self.getTotalTIMDsForScoutName(scout, temp))})
						except:
							pass

			for scout in self.disagreementBreakdown.keys():
				for key in self.disagreementBreakdown[scout].keys():
					if type(self.disagreementBreakdown[scout][key]) == dict:
						for item in self.disagreementBreakdown[scout][key]:
							if type(self.disagreementBreakdown[scout][key][item]) == dict:
								for item2 in self.disagreementBreakdown[scout][key][item]:
									avgScout.update({key: {item: {item2: avgScout.get(key, {}).get(item, {}).get(item2, [] + [self.disagreementBreakdown[scout][key][item][item2]])}}})
							else:
								avgScout.update({key: {item: avgScout.get(key, {}).get(item, []) + [self.disagreementBreakdown[scout][key][item]]}})
					else:
						avgScout.update({key: avgScout.get(key, []) + [self.disagreementBreakdown[scout][key]]})
			for key in avgScout.keys():
				if type(avgScout[key]) == dict:
					for key2 in avgScout[key].keys():
						if type(avgScout[key][key2]) == dict:
							for key3 in avgScout[key][key2].keys():
								avgScout[key][key2][key3] = np.mean(avgScout[key][key2][key3])
						else:
							avgScout[key][key2] = np.mean(avgScout[key][key2])
				else:
					avgScout[key] = np.mean(avgScout[key])
			self.disagreementBreakdown.update({'avgScout': avgScout})

			# Sets avg score before new scouts are set to 0
			realValues = filter(lambda x: x != -1, self.sprs.values())
			self.avgScore = np.mean(realValues) if realValues else 1

			#Changes all sprs of -1 (someone who somehow has an spr key but no matches) to 0
			for a in self.sprs.keys():
				if self.sprs[a] == -1:
					self.sprs[a] = 0.0
			#Any scout in available without an spr score or without any matches is set to 0
			for a in available:
				if a not in self.sprs.keys():
					self.sprs[a] = 0.0
			self.scoutNumMatches = {scout:self.getTotalTIMDsForScoutName(scout, temp) for scout in self.sprs}
		
			with open('./SPROutput.txt', 'w') as f:
				json.dump(self.sprs, f)
			with open('./SPRBreakdownOutput.txt', 'w') as f:
				json.dump(self.disagreementBreakdown, f)
        
		#If there are no tempTIMDs, everyone is set to 1
		else:
			for a in available:
				self.sprs[a] = 1
		self.scoutNumMatches = {scout: self.getTotalTIMDsForScoutName(scout, temp) for scout in self.sprs.keys()}

	#Scout Assignment

	#Orders available scouts by spr ranking, then makes a list of how frequently each scout should be selected
	#Better (lower scoring) scouts appear more frequently
	def getScoutRankingGroups(self, available):
		#Sorts scouts by spr score
		#It is reversed so the scouts with lower spr are later, causing them to be repeated more
		rankedScouts = sorted(available, key = lambda k: self.sprs[k])
		#Lower sprs, so higher number list index scouts are repeated more frequently, but less if there are more scouts
		return [rankedScouts[x : x + 6] for x in range(0, len(rankedScouts), 6)]

	def organizeScouts(self, available, currentTeams, scoutSpots):
		zeroSPRs = []
		# Temporarily sets scouts with no matches to the average SPR for assignments
		for scout in self.sprs.keys():
			if self.sprs[scout] == 0.0 and self.scoutNumMatches[scout] == 0:
				self.sprs[scout] = self.avgScore
				zeroSPRs.append(scout)
		#Picks a random member of the inputted group
		groupFunc = lambda l: l[random.randint(0, (len(l) - 1))]
		#Creates list of groupings that the scouts could be in, with as many scouts as are available and have spaces, for 6 robots with a max group size of 3
		grpCombosList = utils.sum_to_n(min(len(available), (self.numTablets - len(self.unusedTablets))), 4)
		#Picks a random grouping of scouts that, if possible, has an even number of scouts per team
		NoOneCombos = filter(lambda l: 1 not in l, grpCombosList)
		NoTwoCombos = filter(lambda l: 2 not in l, NoOneCombos)
		
		if len(NoTwoCombos) > 0:
			scoutsPGrp = groupFunc(NoTwoCombos)
		elif len(NoOneCombos) > 0:
			scoutsPGrp = groupFunc(NoOneCombos)
		else:
			scoutsPGrp = groupFunc(grpCombosList)
		
		#Since scout groups are reversed, smaller groups come first, so are picked first, so tend to have better scouts
		scoutsPGrp.reverse()
		#Used to make better scouts more likely to be picked
		scouts = []
		rankingGroups = self.getScoutRankingGroups(available)
		#Chooses the correct number of nonrepeating scouts for each group of scouts (of size 1, 2, or 3)
		for c in scoutsPGrp:
			newGroup = self.group(c, rankingGroups)
			scouts += [newGroup]
			rankingGroups = self.removeUsedScouts(rankingGroups, newGroup)
		
		# Resets scouts who had no matches to an SPR of 0
		for scout in zeroSPRs:
			self.sprs[scout] = 0.0

		#Returns the scouts grouped and paired to robots
		return self.scoutsToRobotNums(scouts, currentTeams)

	def group(self, c, rankingGroups):
		finalScouts = []
		for scoutNum in range(c):
			finalScouts.append(random.choice(rankingGroups[scoutNum]))
		return finalScouts

	def removeUsedScouts(self, orderedScouts, removedGroup):
		for index, group in enumerate(orderedScouts):
			for scout in group:
				if scout in removedGroup:
					del orderedScouts[index][group.index(scout)]
		return orderedScouts

	#Assigns a list of scouts to a list of robots in order, and returns as a single dict
	def scoutsToRobotNums(self, scouts, currentTeams):
		f = lambda s: {scouts[s] : currentTeams[s]} if type(scouts[s]) != list else self.mapKeysToValue(scouts[s], currentTeams[s])
		scoutAndNums = map(f, range(len(scouts)))
		return {k : v for l in scoutAndNums for k, v in l.items()}

	#Makes a dict with the same value attached to each inputted key
	def mapKeysToValue(self, keys, value):
		return {k : value for k in keys}

	#Picks a random member of a group, and also returns a list of mambers not picked
	def getRandomIndividuals(self, freqs):
		index = random.randint(0, len(freqs) - 1)
		scout = freqs[index]
		freqs = filter(lambda name: name != scout, freqs)
		return scout, freqs

	def deleteUnassigned(self, d, available):
		for scout in dict(d).keys():
			if scout not in available:
				d[scout]['team'] = -1
				d[scout]['alliance'] = 'red'
		return d

	def getScoutNumFromName(self, name, scoutsInRotation):
		try:
			return filter(lambda k: scoutsInRotation[k].get('mostRecentUser') == name, scoutsInRotation.keys())[0]
		except:
			pass

	def getScoutNameFromNum(self, name, scoutsInRotation):
		return scoutsInRotation[str(name)]['currentUser']

	def getTeamColor(self, team, redTeams, blueTeams):
		if team in redTeams:
			return 'red'
		elif team in blueTeams:
			return 'blue'
		else:
			return 'error'

	#Returns the first scout key that doesn't have a current user
	def findEmptySpotsForScout(self, scoutRotatorDict, available):
		scoutRotatorDict = {dic:data for dic,data in scoutRotatorDict.items() if dic not in self.unusedTablets}
		emptyScouts = filter(lambda k: scoutRotatorDict[k].get('currentUser') == None, scoutRotatorDict.keys())
		emptyScouts += filter(lambda k: scoutRotatorDict[k].get('currentUser') == '', scoutRotatorDict.keys())
		emptyScouts += filter(lambda k: scoutRotatorDict[k].get('currentUser') not in available, scoutRotatorDict.keys())
		return emptyScouts

	#Updates a dict going to firebase with information about scouts for the next match
	def assignScoutsToRobots(self, available, currentTeams, scoutRotatorDict, redTeams, blueTeams):
		namesOfScouts = [name for name in scoutRotatorDict.keys() if name != (None or '')]
		scoutSpots = len(scoutRotatorDict.keys())
		#Assigns available scouts to robots, and shows exactly which available scouts will be scouting
		teams = self.organizeScouts(available, currentTeams, scoutSpots)
		teamColors = {team: self.getTeamColor(team, redTeams, blueTeams) for team in teams.values()}
		for scout in available:
			#Each available scout is put into the dict to send to firebase, in an appropriate spot and with a team number
			scoutRotatorDict = self.assignScoutToRobot(scout, teams, scoutRotatorDict, available, namesOfScouts, teamColors)
		return scoutRotatorDict

	#Finds a spot and a robot for an inputted available scout
	def assignScoutToRobot(self, availableScout, teams, scoutRotatorDict, available, names, teamColors):
		#If the available scout already has a spot on firebase, all that needs to be updated is the robot they scout for
		if availableScout in names:
			scoutRotatorDict[availableScout].update({'team': teams[availableScout], 'alliance':teamColors[teams[availableScout]]})
		#If they don't, it needs to find an empty scout spot in firebase and put the available scout there (if there is an empty spot, which there always should be)
		else:
			# Shouldn't ever run, right?
			scoutRotatorDict[availableScout].update({'team': teams[availableScout], 'alliance':teamColors[teams[availableScout]]})
		return scoutRotatorDict

	#Records z-scores of each scouts spr, for later checking and comparison
	def sprZScores(self, PBC):
		if self.sprs.values():
			if np.std(self.sprs.values()) == 0:
				zscores = {k : (0.0, self.sprs[k], self.scoutNumMatches[k]) for k in self.sprs.keys()}
			else:
				zscores = {k : (zscore, self.sprs[k], self.scoutNumMatches[k]) for (k, zscore) in zip(self.sprs.keys(), stats.zscore(self.sprs.values()))}
			CSVExporter.CSVExportScoutZScores(zscores)
