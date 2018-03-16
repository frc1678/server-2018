#Last Updated: 2/15/18
import pyrebase
import DataModel
import SPR
import firebaseCommunicator
import time
import traceback
import CrashReporter
import pprint
import json

SPR = SPR.ScoutPrecision()
PBC = firebaseCommunicator.PyrebaseCommunicator()
fb = PBC.firebase
global oldMatchNum
oldMatchNum = fb.child('currentMatchNum').get().val()

numScouts = 24
scouts = 'Carl Justin Calvin Aakash Aidan Anoushka Asha Carter Eli Emily Freddy Hanson Jack James Joey Kenny Lyra Rolland Stephen Teo Tim Zach Zatara Zoe'.split()

#Creates list of availability values in firebase for each scout
def resetAvailability():
	availability = {name: 1 for name in scouts}
	fb.child('availability').set(availability)

#Creates firebase objects for 18 scouts
def resetScouts():
	scoutsList = {'scout' + str(num) : {'currentUser': '', 'scoutStatus': ''} for num in range(1, 19)}
	fb.child('scouts').set(scoutsList)

#Sets scouts which are not set yet on firebase
def setNotSetScouts(scoutsAlreadySet):
	scoutsList = {'scout' + str(num) : {'currentUser': scouts[num - 1], 'scoutStatus': 'requested'} for num in range(1, 19)}
	print(scoutsList)
	for i in scoutsList:
		if i in scoutsAlreadySet:
			del i
	fb.child('scouts').set(scoutsList)

#Main function for scout assignment
def doSPRsAndAssignments(data):
	#Wait until the availability has been confirmed to be correct
	while(True):
		try:
			availabilityUpdated = fb.child('availabilityUpdated').get().val()
		except KeyboardInterrupt:
			return
		except:
			availabilityUpdated = 0
		if availabilityUpdated: break
		time.sleep(2)
	try:
		fb.child('availabilityUpdated').set(0)
		#if data.get('data') == None: return
		#Gets scouting data from firebase
		newMatchNumber = str(fb.child('currentMatchNum').get().val())
		print('Setting scouts for match', str(newMatchNumber))
		scoutDict = fb.child('scouts').get().val()
		#Gets the teams we need to scout for the upcoming match
		blueTeams = fb.child('Matches').child(newMatchNumber).get().val()['blueAllianceTeamNumbers']
		redTeams = fb.child('Matches').child(newMatchNumber).get().val()['redAllianceTeamNumbers']
		print(redTeams + blueTeams)
		#Finds and assigns available scouts
		available = [k for (k, v) in fb.child('availability').get().val().items() if v == 1]
		#Grades scouts and assigns them to robots
		SPR.calculateScoutPrecisionScores(fb.child('TempTeamInMatchDatas').get().val(), available)
		SPR.sprZScores(PBC)
		with open('./disagreementBreakdownExport.json', 'w') as file:
			json.dump(SPR.disagreementBreakdown, file)
		newAssignments = SPR.assignScoutsToRobots(available, redTeams + blueTeams, scoutDict)
		#And it is put on firebase
		fb.child('scouts').update(newAssignments)
		print('New Assignments added')
	except KeyboardInterrupt:
		return
	except:
		print(traceback.format_exc())
		# CrashReporter.reportServerCrash(traceback.format_exc())

#Use this to reset scouts and availability before assigning tablets
#e.g. at the beginning of the day at a competition
def tabletHandoutStream():
	resetScouts()
	resetAvailability()
	fb.child('currentMatchNum').stream(doSPRsAndAssignments)

def startAtNewMatch(newMatchNum):
	global oldMatchNum
	if fb.child('currentMatchNum').get().val() > oldMatchNum:
		doSPRsAndAssignments(newMatchNum)

#Assign Scouts and Tablet Handouts- reset ALL scouts at beggining of day in a comp
def notSimpleStream():
	global oldMatchNum
	fb.child('currentMatchNum').get().val()
	oldScoutNames = [fb.child('scouts').child('scout' + str(num)).child('currentUser').get().val() for num in range(1, 19)]
	scoutsAlreadySet = set(oldScoutNames)
	if len(scoutsAlreadySet) >= 19:
		#If it's good, it's good. -Kenny 2k18
		print(scoutsAlreadySet)
		print('It\'s Good')
	else:
		#Otherwise, it's not good.
		setNotSetScouts(scoutsAlreadySet)
		fb.child('currentMatchNum').stream(startAtNewMatch)
	if oldScoutNames == []:
		#If there are no scoutNames, then we have stuff to do
		resetScouts()
		resetAvailability()
		fb.child('currentMatchNum').stream(doSPRsAndAssignments)

#Use this if you are restarting the server and need to reassign scouts but scouts already have tablets
#Also useful for unexpected changes in availability
def simpleStream():
	fb.child('currentMatchNum').stream(doSPRsAndAssignments)

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
