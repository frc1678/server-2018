#Last Updated: 2/9/18
import utils
import Math
import random
import numpy as np
import scipy.stats as stats
import CSVExporter
import pprint

#Scout Performance Analysis
class ScoutPrecision(object):
	'''Scores and ranks scouts and assigns them to robots'''
	def __init__(self):
		super(ScoutPrecision, self).__init__()
		self.sprs = {}
		self.robotNumToScouts = []
		#These keys are the names of sections of the tempTIMDs on which scouts will be graded
		#The value is the weight, since some data points are more important than others
		self.gradingKeys = {
			'didCrossAutoZone': 1.5,
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

	#SPR
	#Scout precision rank(ing): checks accuracy of scouts by comparing their past TIMDs to the consensus
	#Outputs list of TIMDs that an inputted scout was involved in
	def getTotalTIMDsForScoutName(self, scoutName, tempTIMDs):
		return len(filter(lambda v: v.get('scoutName') == scoutName, tempTIMDs.values()))

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
		scouts = filter(lambda v: v, map(lambda k: k.get('scoutName'), tempTIMDs))
		#Finds values (at an inputted key) in tempTIMDs
		values = filter(lambda v: v != None, map(lambda t: t[key] if t.get('scoutName') else None, tempTIMDs))
		#Finds the most common value in the list of values, or the average if none of them is the majority
		valueFrequencies = map(values.count, values)
		if values:
			commonValue = values[valueFrequencies.index(max(valueFrequencies))]
			#If less than half of the values agree, SPR should not be affected
			if values.count(commonValue) <= len(values) / 2:
				commonValue = None
			if commonValue:
				#Makes a list of the differences from the common value multiplied by weight, for relative importance of data points
				differenceFromCommonValue = map(lambda v: weight, values)
				#Adds the difference from this tempTIMD for this key to each scout's previous differences (spr score)
				for c in range(len(differenceFromCommonValue)):
					#Gets inaccuracy by category
					self.SPRBreakdown.update({key: (self.SPRBreakdown.get(key) or []) + [(differenceFromCommonValue[c])]})
					#Gets disagreements by category and scout
					if differenceFromCommonValue[c] != 0:
						self.disagreementBreakdown[scouts[c]].update({key: (self.disagreementBreakdown[scouts[c]].get(key) or 0) + 1})
					else:
						self.disagreementBreakdown[scouts[c]].update({key: (self.disagreementBreakdown[scouts[c]].get(key) or 0)})
				self.sprs.update({scouts[c] : (self.sprs.get(scouts[c]) or 0) + differenceFromCommonValue[c] for c in range(len(differenceFromCommonValue))})

	def findOddScoutForDict(self, tempTIMDs, key):
		#Similar to findOddScoutForDataPoint, but for each data point inside of a dict
		weight = self.gradingDicts[key]
		scouts = filter(lambda v: v, map(lambda k: k.get('scoutName'), tempTIMDs))
		#print('t', tempTIMDs)
		#print('key', key)

		# Not used 2018, needs changes to weight items in a dict differently if used
		'''
		for x in tempTIMDs:
			print('x', x)
			#print('t', type(x[key]))
			try:
				print(x[key] if t.get('scoutName') else None)
				print('success')
			except:
				pass
				tempTIMDs[ tempTIMDs.index(x) ][key] = None
				print('setnone', key)
		'''
		dicts = filter(lambda k: k, map(lambda t: t[key] if t.get('scoutName') else None, tempTIMDs))
		#print(dicts)
		if dicts:
			#print('d', dicts)
			#Compares each key within the dict
			#print('k', dicts[0].keys())
			for key in dicts[0].keys():
				values = []
				for aDict in dicts:
					values += [aDict[key]]
				#Same thing as
				# values = list(filter(lambda aDict: [aDict[key]], dicts))
				
				#See descriptions in findOddScoutForDataPoint for this section (comparing data on each key)
				valueFrequencies = map(values.count, values)
				commonValue = values[valueFrequencies.index(max(valueFrequencies))]
				if values.count(commonValue) <= len(values) / 2:
					commonValue = np.mean(values)
				differenceFromCommonValue = map(lambda v: abs(v - commonValue) * weight, values)
				for c in range(len(differenceFromCommonValue)):
					#Gets inaccuracy by category
					self.SPRBreakdown.update({key: (self.SPRBreakdown.get(key) or []) + [(differenceFromCommonValue[c] / weight)]})
					#Gets disagreements by category and scout
					if differenceFromCommonValue[c] != 0:
						self.disagreementBreakdown[scouts[c]].update({key: (self.disagreementBreakdown[scouts[c]].get(key) or 0) + 1})
					else:
						self.disagreementBreakdown[scouts[c]].update({key: (self.disagreementBreakdown[scouts[c]].get(key) or 0)})
				self.sprs.update({scouts[c] : (self.sprs.get(scouts[c]) or 0) + differenceFromCommonValue[c] for c in range(len(differenceFromCommonValue))})

	def findOddScoutForListOfDicts(self, tempTIMDs, key1):
		#Similar to findOddScoutForDict, but for lists of several dicts instead of individual dicts
		#The nth dict on each list should be the same
		weight = self.gradingListsOfDicts[key1][0]
		allScouts = filter(lambda v: v, map(lambda k: k.get('scoutName'), tempTIMDs))
		# Unsorted meaning they can have different lengths
		unsortedLists = filter(lambda k: k, map(lambda t: t.get(key1) if t.get('scoutName') else None, tempTIMDs))
		#Finds the mode for length of dicts and ignores if not that length
		#i.e. if there is disagreement over how many shots a robot took
		if unsortedLists:
			modeListLength = max(set(map(len,unsortedLists)), key=map(len,unsortedLists).count) # finds mode, not max
			modeAmount = map(len,unsortedLists).count(modeListLength)
			#If someone missed an attempt or had an extra attempt, there is no way to compare their data
			#This filters out anything with a different length of dicts
			# 2018 - each dict is an attempt
			lists = []
			scouts = []
			for aScoutIndex in range(len(unsortedLists)):
				if len(unsortedLists[aScoutIndex]) == modeListLength:
					lists.append(unsortedLists[aScoutIndex])
					scouts.append(allScouts[aScoutIndex])
				elif modeAmount > 1: # Updates SPR if incorecct list amount and at least 2 scouts agree
					self.sprs.update({allScouts[aScoutIndex]: (self.sprs.get(allScouts[aScoutIndex]) or 0) + weight})
			# Need at least 2 scouts to compare, or SPR is not affected
			if modeAmount > 1:
				for num in range(modeListLength):
					#Comparing dicts that should be the same (e.g. each shot time dict for the same shot) within the tempTIMDs
					#This means the nth shot by a given robot in a given match, as recorded by multiple scouts
					#The comparison itself is the same as the other findOddScout functions
					dicts = [lis[num] for lis in lists]
					for key2 in dicts[0].keys():
						#Strings can be averaged (we're just looking at mean, not subtracting them)
						#Without averaging, one person could be declared correct for no reason
						values = []
						for aDict in dicts:
							values += [aDict[key2]]
						#Same thing as
						# values = list(filter(lambda aDict: [aDict[key2]], dicts))
						weight = self.gradingListsOfDicts[key1][1][key2]
						if weight != 0.0:
							valueFrequencies = map(values.count, values)
							commonValue = values[valueFrequencies.index(max(valueFrequencies))]
							if values.count(commonValue) <= len(values) / 2:
								commonValue = np.mean(values)
							differenceFromCommonValue = map(lambda v: weight if v != commonValue else 0, values)
							#Gets inaccuracy by category
							for c in range(len(differenceFromCommonValue)):
								self.SPRBreakdown.update({key2: (self.SPRBreakdown.get(key2) or []) + [(differenceFromCommonValue[c])]})
							self.sprs.update({scouts[c] : (self.sprs.get(scouts[c]) or 0) + differenceFromCommonValue[c] for c in range(len(differenceFromCommonValue))})

	def findOddScoutForListOfDictsDicts(self, tempTIMDs, key1):
		# Similar to findOddScoutForListOfDicts, but for a (dict in dict) in a list
		#The nth dict on each list should be the same
		weight = self.gradingListsOfDictsDicts[key1][0]
		allScouts = filter(lambda v: v, map(lambda k: k.get('scoutName'), tempTIMDs))
		# Unsorted meaning they can have different lengths
		unsortedLists = filter(lambda k: k, map(lambda t: t.get(key1) if t.get('scoutName') else None, tempTIMDs))
		#Finds the mode for length of dicts and ignores if not that length
		#i.e. if there is disagreement over how many shots a robot took
		if unsortedLists:
			modeListLength = max(set(map(len,unsortedLists)), key=map(len,unsortedLists).count) # finds mode, not max
			modeAmount = map(len,unsortedLists).count(modeListLength)
			#If someone missed an attempt or had an extra attempt, there is no way to compare their data
			#This filters out anything with a different length of dicts
			# 2018 - each dict is an attempt
			lists = []
			scouts = []
			for aScoutIndex in range(len(unsortedLists)):
				if len(unsortedLists[aScoutIndex]) == modeListLength:
					lists.append(unsortedLists[aScoutIndex])
					scouts.append(allScouts[aScoutIndex])
				elif modeAmount > 1: # Updates SPR if incorecct list amount and at least 2 scouts agree
					self.sprs.update({allScouts[aScoutIndex]: (self.sprs.get(allScouts[aScoutIndex]) or 0) + weight})
			# Need at least 2 scouts to compare, or SPR is not affected
			if modeAmount > 1:
				for num in range(modeListLength):
					#Comparing dicts that should be the same (e.g. each shot time dict for the same shot) within the tempTIMDs
					#This means the nth shot by a given robot in a given match, as recorded by multiple scouts
					#The comparison itself is the same as the other findOddScout functions
					dicts = [lis[num] for lis in lists]

					keys = []
					for x in dicts:
						keys.append(x.keys()[num])
					modeKey = max(set(keys), key=keys.count)
					modeKeyAmount = keys.count(modeKey)

					dicts2 = []
					scouts2 = []
					weight = self.gradingListsOfDictsDicts[key1][1]
					for index in range(len(dicts)):
						if dicts[index].keys()[num] == modeKey:
							dicts2.append(dicts[index])
							scouts2.append(scouts[index])
						else:
							self.sprs.update({scouts[index]: (self.sprs.get(scouts[index]) or 0) + weight})
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
									valueFrequencies = map(values.count, values)
									commonValue = values[valueFrequencies.index(max(valueFrequencies))]
									if values.count(commonValue) <= len(values) / 2:
										commonValue = np.mean(values)
									differenceFromCommonValue = map(lambda v: weight if v != commonValue else 0, values)
									#Gets inaccuracy by category
									for c in range(len(differenceFromCommonValue)):
										self.SPRBreakdown.update({key2: (self.SPRBreakdown.get(key2) or []) + [(differenceFromCommonValue[c])]})
									self.sprs.update({scouts2[c] : (self.sprs.get(scouts2[c]) or 0) + differenceFromCommonValue[c] for c in range(len(differenceFromCommonValue))})


	def calculateScoutPrecisionScores(self, temp, available):
		if temp:
			#Combines all tempTIMDs for the same match
			g = self.consolidateTIMDs(temp)
			#Makes a list of scouts with data
			priorScouts = []
			for timd in g.values():
			 	for ind in timd:
					priorScouts += [ind['scoutName']]
			#Same thing as
			# priorScouts = list(filter(lambda timd: filter(lambda ind: ind['scoutName'], timd), g.values()))
			
			priorScouts = set(priorScouts) #updates priorScouts so that one scoutName cannot appear more than once
			for scout in priorScouts:
				self.disagreementBreakdown.update({scout: {}})
			#Removes any data from previous calculations from sprs
			self.sprs = {}
			'''These three grade each scout for each of the values in the grading keys, dicts, and lists of dicts
			Each scout gets more 'points' if they are further off from the consensus on the actual values
			The grades are stored by scout name in sprs
			See the findOddScout functions for details on how'''
			[self.findOddScoutForDataPoint(v, k) for v in g.values() for k in self.gradingKeys.keys()]
			#[self.findOddScoutForDict(v, k) for v in g.values() for k in self.gradingDicts.keys()] # Not used 2018, needs changes
			[self.findOddScoutForListOfDicts(v, k) for v in g.values() for k in self.gradingListsOfDicts.keys()]
			[self.findOddScoutForListOfDictsDicts(v, k) for v in g.values() for k in self.gradingListsOfDictsDicts.keys()]
			'''Divides values for scouts by number of TIMDs the scout has participated in
			If a scout is in more matches, they will likely have more disagreements, but the same number per match if they are equally accurate
			If someone has no tempTIMDs (but still an SPR key somehow), their SPR score is set to -1 (changed in the next section)'''
			self.sprs = {k:((v / float(self.getTotalTIMDsForScoutName(k, temp))) or -1) for (k, v) in self.sprs.items()}
			#Makes an average number of disagreements per scout per category
			avgScout = {}
			for scout in self.disagreementBreakdown.keys():
				for key in self.disagreementBreakdown[scout].keys():
					try:
						self.disagreementBreakdown[scout].update({key: float(self.disagreementBreakdown[scout][key]) / float(self.getTotalTIMDsForScoutName(scout, temp))})
					except:
						pass
			for scout in self.disagreementBreakdown.keys():
				for key in self.disagreementBreakdown[scout].keys():
					avgScout.update({key: (avgScout.get(key) or []) + [self.disagreementBreakdown[scout][key]]})
			for key in avgScout.keys():
				avgScout[key] = np.mean(avgScout[key])
			self.disagreementBreakdown.update({'avgScout': avgScout})
			
			#Changes all sprs of -1 (someone who somehow has an spr key but no matches) to average or 1
			for a in self.sprs.keys():
				if self.sprs[a] == -1:
					realValues = filter(lambda x: x != -1, self.sprs.values())
					avgScore = np.mean(realValues) if realValues else 1
					self.sprs[a] = avgScore
			#Any scout in available without an spr score or without any matches is set to the average score or 1
			for a in available:
				if a not in self.sprs.keys():
					avgScore = np.mean(self.sprs.values()) if self.sprs else 1
					self.sprs[a] = avgScore
		#If there are no tempTIMDs, everyone is set to 1
		else:
			for a in available:
				self.sprs[a] = 1

	#Scout Assignment

	#Orders available scouts by spr ranking, then makes a list of how frequently each scout should be selected
	#Better (lower scoring) scouts appear more frequently
	def getScoutFrequencies(self, available):
		#Sorts scouts by spr score
		#It is reversed so the scouts with lower spr are later, causing them to be repeated more
		rankedScouts = sorted(self.sprs.keys(), key = lambda k: self.sprs[k])
		#Lower sprs, so higher number list index scouts are repeated more frequently, but less if there are more scouts
		func = lambda s: [s] * (rankedScouts.index(s) + 1) * ((100 / (len(rankedScouts) + 1)) + 1)
		return utils.extendList(map(func, available))

	def organizeScouts(self, available, currentTeams, scoutSpots):
		#Picks a random member of the inputted group
		groupFunc = lambda l: l[random.randint(0, len(l) - 1)]
		#Creates list of groupings that the scouts could be in, with as many scouts as are available and have spaces, for 6 robots with a max group size of 3
		grpCombos = utils.sum_to_n(min(len(available), scoutSpots), 6, 3)
		grpCombosList = [combo for combo in grpCombos]
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
		freqs = self.getScoutFrequencies(available)
		scouts = []
		#Chooses the correct number of nonrepeating scouts for each group of scouts (of size 1, 2, or 3)
		for c in scoutsPGrp:
			newGroup = self.group(freqs, c)
			scouts += [newGroup[0]]
			freqs = newGroup[1]
		#Returns the scouts grouped and paired to robots
		return self.scoutsToRobotNums(scouts, currentTeams)

	#Assigns a list of scouts to a list of robots in order, and returns as a single dict
	def scoutsToRobotNums(self, scouts, currentTeams):
		f = lambda s: {scouts[s] : currentTeams[s]} if type(scouts[s]) != list else self.mapKeysToValue(scouts[s], currentTeams[s])
		scoutAndNums = map(f, range(len(scouts)))
		return {k : v for l in scoutAndNums for k, v in l.items()}

	#Makes a dict with the same value attached to each inputted key
	def mapKeysToValue(self, keys, value):
		return {k : value for k in keys}

	#Picks an inputted number of random non-repeating members for a group, and also returns the list of members not picked
	def group(self, availableForGroup, count):
		toReturn = []
		for num in range(count):
			newMember = availableForGroup[random.randint(0, len(availableForGroup) - 1)]
			availableForGroup = filter(lambda m: m != newMember, availableForGroup)
			toReturn += [newMember]
		return toReturn, availableForGroup

	#Picks a random member of a group, and also returns a list of mambers not picked
	def getRandomIndividuals(self, freqs):
		index = random.randint(0, len(freqs) - 1)
		scout = freqs[index]
		freqs = filter(lambda name: name != scout, freqs)
		return scout, freqs

	def getScoutNumFromName(self, name, scoutsInRotation):
		return filter(lambda k: scoutsInRotation[k].get('mostRecentUser') == name, scoutsInRotation.keys())[0]

	#Returns the first scout key that doesn't have a current user
	def findEmptySpotsForScout(self, scoutRotatorDict, available):
		emptyScouts = filter(lambda k: scoutRotatorDict[k].get('currentUser') == None, scoutRotatorDict.keys())
		emptyScouts += filter(lambda k: scoutRotatorDict[k].get('currentUser') == '', scoutRotatorDict.keys())
		emptyScouts += filter(lambda k: scoutRotatorDict[k].get('currentUser') not in available, scoutRotatorDict.keys())
		return emptyScouts

	#Updates a dict going to firebase with information about scouts for the next match
	def assignScoutsToRobots(self, available, currentTeams, scoutRotatorDict):
		scoutsWithNames = filter(lambda v: v.get('currentUser') != (None or ''), scoutRotatorDict.values())
		namesOfScouts = map(lambda v: v.get('currentUser'), scoutsWithNames)
		scoutSpots = len(scoutRotatorDict.keys())
		#Assigns available scouts to robots, and shows exactly which availabe scouts will be scouting
		teams = self.organizeScouts(available, currentTeams, scoutSpots)
		available = teams.keys()
		#Moves the current user to the previous user spot, assigns a new user if necessary, and assigns a robot to each scout
		for scout in scoutRotatorDict.keys():
			#The current user is now the previous user, as the match has changed
			if scoutRotatorDict[scout].get('currentUser'):
				oldName = scoutRotatorDict[scout]['currentUser']
				scoutRotatorDict[scout].update({'mostRecentUser': oldName})
				if oldName not in available:
					#If they are not scouting again, team and current user are deleted, since either that scout spot will be empty this match or someone else will be put there
					scoutRotatorDict[scout].update({'team': None, 'currentUser': None})
		for scout in available:
			#Each available scout is put into the dict to send to firebase, in an appropriate spot and with a team number
			scoutRotatorDict = self.assignScoutToRobot(scout, teams, scoutRotatorDict, available, namesOfScouts)
		return scoutRotatorDict

	#Finds a spot and a robot for an inputted available scout
	def assignScoutToRobot(self, availableScout, teams, scoutRotatorDict, available, names):
		namesToNumbers = [' ','Jon','Jim','Bob','Bill','Joe','Bran','Ken','Mat','Dog','End','Mrs','Hi','Death','The','Adhoc','Pro','001','Ergo']
		#If the available scout already has a spot on firebase, all that needs to be updated is the robot they scout for
		if availableScout in names:
			scoutNum = self.getScoutNumFromName(availableScout, scoutRotatorDict)
			scoutRotatorDict[scoutNum].update({'team': teams[availableScout], 'currentUser': availableScout, 'scoutStatus': 'requested'})
		#If they don't, it needs to find an empty scout spot in firebase and put the available scout there (if there is an empty spot, which there always should be)
		else:
			newSpace = 'scout' + str(namesToNumbers.index(availableScout))			scoutRotatorDict[newSpace].update({'team': teams[availableScout], 'currentUser': availableScout, 'scoutStatus': 'requested'})
		return scoutRotatorDict

	#Records z-scores of each scouts spr, for later checking and comparison
	def sprZScores(self, PBC):
		if np.std(self.sprs.values()) == 0:
			zscores = {k : (0.0, self.sprs[k]) for k in self.sprs.keys()}
		else:
			zscores = {k : (zscore, self.sprs[k]) for (k, zscore) in zip(self.sprs.keys(), stats.zscore(self.sprs.values()))}
		CSVExporter.CSVExportScoutZScores(zscores)
		PBC.sendExport('SPRExport.csv')
