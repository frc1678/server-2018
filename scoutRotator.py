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
scouts = 'Justin Joey Amanda Anoushka Zoe Rolland Teo Hanson Jack Tim Calvin Asha Erik James Carl Freddy Carter Kenny Emily Eli Stephen Aidan Lyra Aakash'.split()

#Creates list of availability values in firebase for each scout
def resetAvailability():
	availability = {name: 1 for name in scouts}
	fb.child('availability').set(availability)

#Creates firebase objects for 18 scouts
def resetScouts():
	scouts = []
	for scout in fb.child('availability').get().val().keys():
		scouts.append(scout)
	fb.child('scouts/assignments').set({scout:{'team':-1,'alliance':'red'} for scout in scouts})
	fb.child('scouts/match').set(fb.child('currentMatchNum').get().val())


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
		scoutDict = fb.child('scouts/assignments').get().val()
		#Gets the teams we need to scout for the upcoming match
		blueTeams = fb.child('Matches').child(newMatchNumber).get().val()['blueAllianceTeamNumbers']
		redTeams = fb.child('Matches').child(newMatchNumber).get().val()['redAllianceTeamNumbers']
		#Finds and assigns available scouts
		available = [k for (k, v) in fb.child('availability').get().val().items() if v == 1]
		if len(available) > (SPR.numTablets - len(SPR.unusedTablets)):
			print('There are too many scouts!')
			print('Please set the availablility!')
			fb.child('currentMatchNum').set((int(newMatchNumber) - 1))
			return
		#Grades scouts and assigns them to robots
		SPR.calculateScoutPrecisionScores(fb.child('TempTeamInMatchDatas').get().val(), available)
		SPR.sprZScores(PBC)
		with open('./disagreementBreakdownExport.json', 'w') as file:
			json.dump(SPR.disagreementBreakdown, file)
		print(SPR.sprs)
		newAssignments = SPR.deleteUnassigned(SPR.assignScoutsToRobots(available, redTeams + blueTeams, scoutDict, redTeams, blueTeams), available)
		#And it is put on firebase
		fb.child('scouts/assignments').set(newAssignments)
		fb.child('scouts/match').set(int(newMatchNumber))
		print('New Assignments added')
	except KeyboardInterrupt:
		return
	except:
		print(traceback.format_exc())
		CrashReporter.reportServerCrash(traceback.format_exc())

#Use this to reset scouts and availability before assigning tablets
#e.g. at the beginning of the day at a competition
def tabletHandoutStream():
	resetAvailability()
	resetScouts()
	fb.child('currentMatchNum').stream(doSPRsAndAssignments)

def startAtNewMatch(newMatchNum):
	global oldMatchNum
	if fb.child('currentMatchNum').get().val() > oldMatchNum:
		doSPRsAndAssignments(newMatchNum)

#Assign Scouts and Tablet Handouts- reset ALL scouts at beggining of day in a comp
def notSimpleStream():
	global oldMatchNum
	fb.child('currentMatchNum').get().val()
	oldScoutNames = [fb.child('scouts/assignments').get()]
	scoutsAlreadySet = set(oldScoutNames)
	if len(scoutsAlreadySet) >= 19:
		#If it's good, it's good. -Kenny 2k18
		print(scoutsAlreadySet)
		print('It\'s Good')
	else:
		#Otherwise, it's not good.
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

tabletHandoutStream()