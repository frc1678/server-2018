import pyrebase
import DataModel
import spr
import firebaseCommunicator

PBC = firebaseCommunicator.PyrebaseCommunicator()
PBC.initializeFirebase()
fb = PBC.firebase
#testScouts = "calvin ethan nathan wentao janet carter kenny ryan nate astha astha gemma livy ben".split()
scouts = "janet justin alex wesley kyle mx aiden westley katie jesse jack sage jon ayush sam evan mingyo zoe gemma carter".split()
spr = spr.ScoutPrecision()

#Creates list of availability values in firebase for each scout
def resetAvailability():
	availability = {name: 1 for name in scouts}
	fb.child('availability').set(availability)

#Creates firebase objects for 18 scouts
def resetScouts():
	scouts = {'scout' + str(num) : {'currentUser': '', 'scoutStatus': ''} for num in range(1,19)}
	fb.child('scouts').set(scouts)

def dosprsAndAssignments(newMatchNumber):
	if newMatchNumber.get('data') == None: return
	print('Setting scouts for match ' + str(fb.child('currentMatchNum').get().val()))
	newMatchNumber = str(fb.child('currentMatchNum').get().val())
	scoutDict = fb.child("scouts").get().val()
	#Gets the teams we need to scout for
	blueTeams = fb.child("Matches").child(newMatchNumber).get().val()['blueAllianceTeamNumbers']
	redTeams = fb.child("Matches").child(newMatchNumber).get().val()['redAllianceTeamNumbers']
	#These next lines find and assign available scouts
	available = [k for (k, v) in fb.child("availability").get().val().items() if v == 1]
	#Each scout is assigned to a robot in the next 2 lines
	spr.calculateScoutPrecisionScores(fb.child("TempTeamInMatchDatas").get().val(), available)
	spr.sprZScores()
	newAssignments = spr.assignScoutsToRobots(available, redTeams + blueTeams, fb.child("scouts").get().val())
	#And it is updated on firebase
	fb.child("scouts").update(newAssignments)

#Use this to reset scouts and availability before assigning tablets
#e.g. at the beginning of the day at a competition
def tabletHandoutStream():
	resetScouts()
	resetAvailability()
	fb.child("currentMatchNum").stream(dosprsAndAssignments)

#Use this for running the server again (e.g. after a crash) to avoid reassigning scouts
def alreadyAssignedStream():
	startMatchNum = fb.child("currentMatchNum").get().val()
	newMatchNum = startMatchNum + 1
	fb.child("currentMatchNum").stream(lambda d: startStreamAfterAssignment(d, newMatchNum))

def startStreamAfterAssignment(newNum, newerNum):
	if newNum.get("data") == None: return
	if newNum["data"] == newerNum:
		dosprsAndAssignments(newNum)

#Use this if you are restarting the server and need to reassign scouts but scouts already have tablets
#Also useful for unexpected changes in availability
def simpleStream():
	fb.child("currentMatchNum").stream(dosprsAndAssignments)
