import SPR
import firebaseCommunicator
import settingsCommunicator
import traceback
import pprint
import json

SPR = SPR.ScoutPrecision()
PBC = firebaseCommunicator.PyrebaseCommunicator()
SC = settingsCommunicator.SettingsCommunicator()
fb = PBC.firebase
global oldMatchNum
oldMatchNum = fb.child('currentMatchNum').get().val()

#Replace these names with the names of scouts
scouts = "John Jim Sam Karen Mary Xavier".split()
numScouts = len(scouts)

#Creates list of availability values in firebase for each scout
def resetAvailability():
	availability = {name: 0 for name in scouts}
	fb.child('availability').set(availability)

#Creates firebase objects for 18 scouts
def resetScouts():
	scouts = []
	for scout in fb.child('availability').get().val().keys():
		scouts.append(scout)
	cycleCounter = fb.child('cycleCounter').get().val()
	fb.child('scouts').child('cycle').set(cycleCounter)

#Main function for scout assignment
def doSPRsAndAssignments(data):
	#Wait until the availability has been confirmed to be correct
	try:
		#Finds and assigns available scouts
		available = [k for (k, v) in fb.child('availability').get().val().items() if v == 1]
		if len(available) > (SPR.numTablets - len(SPR.unusedTablets)):
				print('There are too many scouts!')
				print('Please set the availablility!')
				fb.child('currentMatchNum').set((int(newMatchNumber) - 1))
				return
		#Calculates scout precision rankings
		try:
			SPR.calculateScoutPrecisionScores(fb.child('TempTeamInMatchDatas').get().val(), available)
			SPR.sprZScores(PBC)
		except Exception as e:
			#If spr calculation fails, it prints the error, but doesn't intercept with the scoutRotator
			print(e)
		with open('./disagreementBreakdownExport.json', 'w') as file:
			json.dump(SPR.disagreementBreakdown, file)
		SC.firebase.child('SPRs').set(SPR.sprs)
		#Gets scouting data from firebase
		startingMatchNumber = str(fb.child('currentMatchNum').get().val())
		for newMatchNumber in range(int(startingMatchNumber), int(startingMatchNumber) + 10):
			newMatchNumber = str(newMatchNumber)
			print('Setting scouts for match' + str(newMatchNumber))
			tupScouts = fb.child('availability').get().val()
			scoutDict = {scout : {'team' : -1, 'alliance' : 'red'} for scout in [tup for tup in tupScouts]}
			#Gets the teams we need to scout for the upcoming match
			blueTeams = fb.child('Matches').child(newMatchNumber).get().val()['blueAllianceTeamNumbers']
			redTeams = fb.child('Matches').child(newMatchNumber).get().val()['redAllianceTeamNumbers']
			#Grades scouts and assigns them to robots
			newAssignments = SPR.deleteUnassigned(SPR.assignScoutsToRobots(available, redTeams + blueTeams, scoutDict, redTeams, blueTeams), available)
			#And it is put on firebase
			fb.child('scouts/matches/match' + newMatchNumber).set(newAssignments)
		cycle = fb.child('cycleCounter').get().val()
		fb.child('scouts/cycle').set(cycle)
		print('New Assignments added')
	except KeyboardInterrupt:
		return
	except:
		print(traceback.format_exc())

#Use this to reset scouts and availability before assigning tablets
#e.g. at the beginning of the day at a competition
def tabletHandoutStream():
	resetAvailability()
	resetScouts()
	
def startAtNewMatch(newMatchNum):
	global oldMatchNum
	if fb.child('currentMatchNum').get().val() > oldMatchNum:
		doSPRsAndAssignments(newMatchNum)

#Use this if you are restarting the server and need to reassign scouts but scouts already have tablets
#Also useful for unexpected changes in availability
def simpleStream():
	fb.child('cycleCounter').stream(doSPRsAndAssignments)

#Creates and prints a list of average amounts of inaccuracy by category
def sprBreakdownExport():
	available = [k for (k, v) in fb.child('availability').get().val().items() if v == 1]
	SPR.calculateScoutPrecisionScores(fb.child('TempTeamInMatchDatas').get().val(), available)
	breakdownData = SPR.SPRBreakdown
	avgData = {}
	for key in breakdownData.keys():
		avgData[key] = np.mean(breakdownData[key])
	pprint.pprint(avgData)

#Creates and prints the number of disagreements with consensus per match for each scout, and for an average scout
def findScoutDisagreements():
	available = [k for (k, v) in fb.child('availability').get().val().items() if v == 1]
	SPR.calculateScoutPrecisionScores(fb.child('TempTeamInMatchDatas').get().val(), available)
	pprint.pprint(SPR.disagreementBreakdown)

#Finds total numbers of disagreements per match by scout, and sorts scouts by those totals
def sortScoutDisagreements():
	findScoutDisagreements()
	totalDisagreements = {}
	map(lambda scout: totalDisagreements.update({scout: sum(SPR.disagreementBreakdown[scout].values())}))
	pprint.pprint(totalDisagreements)
	pprint.pprint(sorted(totalDisagreements.items(), key = lambda scout: scout[1]))
	pprint.pprint(sorted(SPR.sprs.items(), key = lambda scout: scout[1]))

#Function for doing sprs without assigning scouts
def doSPRs():
	available = [k for (k, v) in fb.child('availability').get().val().items() if v == 1]
	try:
		SPR.calculateScoutPrecisionScores(fb.child('TempTeamInMatchDatas').get().val(), available)
		SPR.sprZScores(PBC)
	except Exception as e:
		#If spr calculation fails, it prints the error, but doesn't intercept with the scoutRotator
		print(e)
	with open('./disagreementBreakdownExport.json', 'w') as file:
		json.dump(SPR.disagreementBreakdown, file)
	SC.firebase.child('SPRs').set(SPR.sprs)
