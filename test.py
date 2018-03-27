import pyrebase
import DataModel
import firebaseCommunicator
import DataModel
import firebaseCommunicator
import TBACommunicator
import utils
import random
import operator
from collections import Counter

TBAC = TBACommunicator.TBACommunicator()
'''
FBC = firebaseCommunicator.PyrebaseCommunicator()
competition = DataModel.Competition(FBC)
competition.eventCode = TBAC.code
competition.PBC.JSONteams = TBAC.makeEventTeamsRequest()
competition.PBC.JSONmatches = TBAC.makeEventMatchesRequest()
competition.PBC.wipeDatabase()
competition.PBC.addCurrentMatchToFirebase()
competition.PBC.addTeamsToFirebase()
competition.PBC.addMatchesToFirebase()
competition.updateTeamsAndMatchesFromFirebase()
competition.PBC.addTIMDsToFirebase(competition.matches) #You need to create the matches and teams before you call this


url = 'scouting-2018-temp'

config = {
	"apiKey": "AIzaSyBXfDygtDWxzyRaLFO75XeGc2xhfvLLwkU ",
    "authDomain": url + ".firebaseapp.com",
    "databaseURL": "https://" + url + ".firebaseio.com",
    "projectId": url,
    "storageBucket": url + ".appspot.com",
    "messagingSenderId": "333426669167"

}
'''
pbc = firebaseCommunicator.PyrebaseCommunicator()
comp = DataModel.Competition(pbc)
db = pbc.firebase
'''
seed = {}
for team in db.child('Teams').get().val():
	seed[team] = db.child('Teams').child(team).child('calculatedData').child('actualNumRPs').get().val()
print(seed)
seed = sorted(seed.items(), key = operator.itemgetter(1))[::-1]
print(seed)
for item in range(len(seed)):
	db.child('Teams').child(seed[item][0]).child('calculatedData').child('actualSeed').set(item + 1)



dc_team = {
		'scoutName' : ['string', 'string', 'string'], #String
		'superNotes' : 'This bot', #String
		'allianceSwitchAttemptAuto' : [
			{
				'didSucceed' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5, #Float
				'status' : 'ownedBlue', #String
				'layer' : 3 #Int
			}
		],
		'allianceSwitchAttemptTele' : [
			{
				'didSucceed' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5, #Float
				'status' : 'ownedRed', #String
				'layer' : 2 #Int
			}
		],
		'climb' : [ {
			'passiveClimb' : {
				'didSucceed' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5 #Float
			},
			'assistedClimb' : {
				'didSucceed' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5 #Float
			},
			'activeLift' : {
				'didSucceed' : True, #Bool 
				'didClimb' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5, #Float
				'partnerLiftType' : 'assisted', #String
				'didFailToLift' : False, #Bool
				'numRobotsLifted' : 2 #Int
			},
			'soloClimb' : {
				'didSucceed' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5 #Float
			}
		} ],
		'didGetDisabled' : False, #Bool
		'didGetIncapacitated' : False, #Bool
		'didMakeAutoRun' : True, #Bool
		'didPark' : False, #Bool
		'numGoodDecisions' : 1, #Int
		'numBadDecisions' : 1, #Int
		'didCrossAutoZone' : True, #Bool
		'alliancePlatformIntakeAuto' : {
			0 : True, #Bool
			1 : True, #Bool 
			2 : True, #Bool
			3 : True, #Bool
			4 : True, #Bool 
			5 : True, #Bool
			},
		'alliancePlatformIntakeTele' : {
			0 : True, #Bool
			1 : True, #Bool 
			2 : True, #Bool
			3 : True, #Bool
			4 : True, #Bool 
			5 : True, #Bool
			},
		'opponentPlatformIntakeTele' : {
			0 : True, #Bool
			1 : True, #Bool 
			2 : True, #Bool
			3 : True, #Bool
			4 : True, #Bool 
			5 : True, #Bool
			},
		'numCubesFumbledAuto' : 1, #Int
		'numCubesFumbledTele' : 1, #Int
		'numExchangeInput' : 1, #Int
		'numGroundIntakeTele' : 1, #Int
		'numGroundPortalIntakeTele' : 1, #Int
		'numHumanPortalIntakeTele' : 1, #Int
		'numGroundPyramidIntakeAuto' : 1,
		'numGroundPyramidIntakeTele' : 1,
		'numElevatedPyramidIntakeAuto' : 1,
		'numElevatedPyramidIntakeTele' : 1,
		'numReturnIntake' : 1, #Int
		'numSpilledCubesAuto' : 1, #Int
		'numSpilledCubesTele' : 1, #Int
		'rankAgility' : 1, #Int
		'rankDefense' : 1, #Int
		'rankSpeed' : 1, #Int
		'startingPosition' : 'left', #String 'left' 'right' or 'center' CHANGED
		'opponentSwitchAttemptTele' : [
			{
				'didSucceed' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5, #Float
				'status' : 'ownedBlue', #String
				'layer' : 1 #Int
			}
		],
		'scaleAttemptAuto' : [
			{
				'didSucceed' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5, #Float
				'status' : 'ownedBlue', #String
				'layer' : 1 #Int
			}
		],
		'scaleAttemptTele' : [
			{
				'didSucceed' : True, #Bool
				'startTime' : 1.5, #Float
				'endTime' : 1.5, #Float
				'status' : 'ownedBlue', #String
				'layer' : 1 #Int
			}
		],

}

var1 = db.child("TeamInMatchDatas").get().each()

for timd in var1:
	db.child('TeamInMatchDatas').child(str(timd.key())).set(dc_team)
	print(timd.key())

dc_calc_team = {
	'numRPs' : 1, #Int
	'numAllianceSwitchSuccessAuto' : 1, #Int
	'numAllianceSwitchSuccessTele' : 1, #Int
	'numAllianceSwitchFailedAuto' : 1, #Int
	'numAllianceSwitchFailedTele' : 1, #Int
	'numOpponentSwitchSuccessTele' : 1, #Int
	'numOpponentSwitchFailedTele' : 1, #Int
	'numScaleSuccessAuto' : 1, #Int
	'numScaleFailedAuto' : 1, #Int
	'numScaleSuccessTele' : 1, #numReturnIntake
	'numScaleFailedTele' : 1, #Int
	'climbTime' : 1, #Float
	'didClimb' : True, #Bool
	'avgAllianceSwitchTimeTele' : 1.5, #Float
	'avgOpponentSwitchTimeTele' : 1.5, #Float
	'avgScaleTimeAuto' : 1.5, #Float
	'avgScaleTimeTele' : 1.5, #Float
	'avgAllianceSwitchTimeAuto' : 1.5, #Float
	'numOpponentPlatformIntakeTele' : 1, #Int
	'numAlliancePlatformIntakeAuto' : 1, #Int
	'numAlliancePlatformIntakeTele' : 1, #Int
	'numCubesPlacedAuto' : 1, #Int
	'numCubesPlacedTele' : 1, #Int
	'numClimbAttempts' : 1, #Int
	'isDysfunctional' : False, #Bool
	'drivingAbility' : 1.5, #Float probably
	'didConflictWithAuto' : True, #Bool	
}

for timd in var1:
	db.child('TeamInMatchDatas').child(str(timd.key())).child('calculatedData').set(dc_calc_team)
	print(timd.key())

print("TeamInMatchDatas done.")



dc_match = {
	'blueCubesForPowerup' : {
		'Boost' : 1, #Int
		'Force' : 1, #Int
		'Levitate' : 1 #Int
	},
	'blueCubesInVaultFinal' : {
		'Boost' : 1, #Int
		'Force' : 1, #Int
		'Levitate' : 1 #Int
	},
	'blueDidAutoQuest' : True, #Bool
	'blueDidFaceBoss' : True, #Bool
	'blueSwitch' : {
		'left' : 'red', #String
		'right' : 'blue' #String
	},
	'redCubesForPowerUp' : None,
	'redCubesForPowerup' : {
		'Boost' : 1, #Int
		'Force' : 1, #Int
		'Levitate' : 1 #Int
	},
	'redCubesInVaultFinal' : {
		'Boost' : 1, #Int
		'Force' : 1, #Int
		'Levitate' : 1 #Int
	},
	'redDidAutoQuest' : True, #Bool
	'redDidFaceBoss' : True, #Bool
	'redSwitch' : {
		'left' : 'blue', #String
		'right' : 'red' #String
	},
	'scale' : {
		'left' : 'blue', #String
		'right' : 'red' #String
	},
	'redScore' : 1, #Int
	'blueScore' : 1, #Int
	'foulPointsGainedRed' : 1, #Int
	'foulPointsGainedBlue' : 1, #Int
}

var2 = db.child("Matches").get().each()

for x, y in dc_match.items():
	for a in var2:
		db.child("Matches/"+str(a.key())+"/"+x).set(y)
	print(x+" done for all teams.")

calcMatch = {
	'predictedBlueScore' : 1.5, #Float
	'predictedRedScore' : 1.5, #Float
	'predictedBlueRPs' : 1.5, #Float
	'actualBlueRPs' : 1, #Int
	'predictedRedRPs' : 1.5, #Float
	'actualRedRPs' : 1, #Int
	'predictedBlueAutoQuest' : True, #Bool
	'predictedRedAutoQuest' : True, #Bool
	'redPredictedPark' : 1.5, #Float
	'bluePredictedPark' : 1.5, #Float
	'redWinChance' : 1.5, #Float
	'blueWinChance' : 1.5, #Float
	'redLevitateProbability' : 1.5, #Float
	'blueLevitateProbability' : 1.5, #Float
	'redTeleopExchangeAbility' : 1.5, #Float
	'redTeleopExchangeAbility' : 1.5, #Float
}

for timd in var2:
	db.child('Matches').child(str(timd.key())).child('calculatedData').set(calcMatch)
	print(timd.key())

print("Matches done.")

dc_teamdata = {
	'numMatchesPlayed' : 1, #Int
	'pitSelectedImage' : None, #String #String
	'pitAvailableWeight' : 1, #Int
	'pitDriveTrain' : 'string', #String #String CHANGED
	'pitCanCheesecake' : True, #Bool
	'pitSEALsNotes' : 'string', #String
	'pitProgrammingLanguage' : 'string', #String
	'pitClimberType' : 'string', #String
	'pitMaxHeight' : 1.5, #Float
	'pitAutoRunTimes' : None, #Float
	'pitAutoRunTime' : None, #Float
	'pitAllImageURLs' : None,
	'pitImageKeys' : None,
	'totalSuperNotes' : ['Thisbot', 'THIDBto', 'hehe', 'botot'],
	'pitRampTime' : [{'didSucceed' : True, 'time' : 1.5}, {'didSucceed' : True, 'time' : 1.5}],
	'pitDriveTime' : [{'didSucceed' : True, 'time' : 1.5}, {'didSucceed' : True, 'time' : 1.5}],
}

var3 = db.child("Teams").get().each()

for x, y in dc_teamdata.items():
	for a in var3:
		print(a.key())
		db.child("Teams/"+str(a.key())+"/"+x).set(y)
	print(x+" done for all teams.")

print("Teams Done.")

teamCalc = {
	'avgNumOpponentPlatformIntakeAuto' : None,
	'avgOpponentSwitchCubesAuto' : None,
	'avgScaleTimeAuto' : 1.5,
	'avgScaleTimeTele' : 1.5,
	'avgAllianceTimeAuto' : None,
	'avgAllianceTimeTele' : None,
	'avgOpponentTimeTele' : None,
	'lfmAvgNumOpponentPlatformIntakeAuto' : None,
	'lfmAvgOpponentSwitchCubesAuto' : None,
	'lfmAvgScaleTimeAuto' : 1.5,
	'lfmAvgScaleTimeTele' : 1.5,
	'lfmAvgAllianceSwitchTimeAuto' : 1.5,
	'lfmAvgAllianceSwitchTimeTele' : 1.5,
	'lfmAvgOpponentSwitchTimeTele' : 1.5,
	'RScoreDefense' : 1.5,
	'RScoreSpeed' : 1.5,
	'RScoreAgility' : 1.5,
	'RScoreDrivingAbility' : 1.5,
	'firstPickAbility' : 1.5, #Float
	'secondPickAbility' : 1.5, #Float
	'disabledPercentage' : 1.5, #Float
	'incapacitatedPercentage' : 1.5, #Float
	'avgNumOpponentPlatformIntakeAuto' : None, #Float
	'avgNumAlliancePlatformIntakeAuto' : 1.5, #Float
	'avgNumGroundPyramidIntakeAuto' : 1.5, #Float
	'avgNumElevatedPyramidIntakeAuto' : 1.5, #Float
	'avgNumCubesFumbledAuto' : 1.5, #Float
	'avgNumCubesFumbledTele' : 1.5, #Float
	'avgNumGroundPyramidIntakeTele' : 1.5, #Float
	'avgNumElevatedPyramidIntakeTele' : 1.5, #Float
	'avgNumOpponentPlatformIntakeTele' : 1.5, #Float
	'avgNumAlliancePlatformIntakeTele' : 1.5, #Float
	'avgNumGroundIntakeTele' : 1.5, #Float
	'avgNumGroundPortalIntakeTele' : 1.5, #Float
	'avgNumHumanPortalIntakeTele' : 1.5, #Float
	'avgNumExchangeInputTele' : 1.5, #Float'
	'avgNumReturnIntakeTele' : 1.5, #Float
	'avgCubesSpilledAuto' : 1.5, #Float
	'avgCubesSpilledTele' : 1.5, #Float
	'avgCubesPlacedInScaleAuto' : 1.5, #Float
	'avgCubesPlacedInScaleTele' : 1.5, #Float
	'avgOpponentSwitchCubesAuto' : None, #Float
	'avgOpponentSwitchCubesTele' : 1.5, #Float
	'avgAllianceSwitchCubesAuto' : 1.5, #Float
	'avgAllianceSwitchCubesTele' : 1.5, #Float
	'avgNumGoodDecisions' : 1.5, #Float
	'avgNumBadDecisions' : 1.5, #Float
	'avgClimbTime' : 1.5, #Float
	'avgAgility' : 1.5, #Float
	'avgSpeed' : 1.5, #Float
	'avgDefense' : 1.5, #Float
	'avgDrivingAbility' : 1.5, #Float
	'lfmAvgNumOpponentPlatformIntakeAuto' : None, #Float
	'lfmAvgNumAlliancePlatformIntakeAuto' : 1.5, #Float
	'lfmAvgNumGroundPyramidIntakeAuto' : 1.5, #Float
	'lfmAvgNumElevatedPyramidIntakeAuto' : 1.5, #Float
	'lfmAvgNumElevatedPyramidIntakeTele' : 1.5, #Float
	'lfmAvgNumCubesFumbledAuto' : 1.5, #Float
	'lfmAvgNumCubesFumbledTele' : 1.5, #Float
	'lfmAvgNumOpponentPlatformIntakeTele' : 1.5, #Float
	'lfmAvgNumAlliancePlatformIntakeTele' : 1.5, #Float
	'lfmAvgNumGroundIntakeTele' : 1.5, #Float
	'lfmAvgNumGroundPortalIntakeTele' : 1.5, #Float
	'lfmAvgNumHumanPortalIntakeTele' : 1.5, #Float
	'lfmAvgNumExchangeInputTele' : 1.5, #Float
	'lfmAvgNumReturnIntakeTele' : 1.5, #Float
	'lfmAvgNumGoodDecisions' : 1.5, #Float
	'lfmAvgNumBadDecisions' : 1.5, #Float
	'lfmAvgCubesSpilledAuto' : 1.5, #Float
	'lfmAvgCubesSpilledTele' : 1.5, #Float
	'lfmAvgCubesPlacedInScaleAuto' : 1.5, #Float
	'lfmAvgCubesPlacedInScaleTele' : 1.5, #Float
	'lfmAvgOpponentSwitchCubesAuto' : None, #Float
	'lfmAvgOpponentSwitchCubesTele' : 1.5, #Float
	'lfmAvgAllianceSwitchCubesAuto' : 1.5, #Float
	'lfmAvgAllianceSwitchCubesTele' : 1.5, #Float
	'lfmAvgSpeed' : 1.5, #Float
	'lfmAvgDefense' : 1.5, #Float
	'lfmAvgAgility' : 1.5, #Float
	'lfmAvgDrivingAbility' : 1.5, #Float
	'totalNumGoodDecisions' : 1, #Int
	'totalNumBadDecisions' : 1, #Int
	'totalNumParks' : 1, #Int
	'totalNumRobotsLifted' : 1, #Int
	'totalNumRobotLiftAttempts' : 1, #Int
	'totalNumRobotsGroundLifted' : 1, #Int
	'totalNumRobotGroundLiftAttempts' : 1, #Int
	'numSuccessfulClimbs' : 1, #Int
	'predictedClimb' : 1.5, #Float CHANGED
	'climbPercentage' : 1.5, #Float
	'predictedNumAllianceSwitchCubesAuto' : 1.5, #Int CHANGED
	'predictedNumScaleCubesAuto' : 1.5, #Float CHANGED
	'actualNumRPs' : 1.5, #Float
	'predictedNumRPs' : 1.5, #Float
	'autoRunPercentage' : 1.5, #Float
	'switchFailPercentageAuto' : None, #Float
	'scaleSuccessPercentageAuto' : 1.5, #Float
	'switchFailPercentageTele' : None, #Float
	'scaleSuccessPercentageTele' : 1.5, #Float
	'canScoreBothSwitchSidesAuto' : True, #Bool
	'allianceSwitchSuccessPercentageAuto' : 1.5, #Float
	'allianceSwitchSuccessPercentageTele' : 1.5, #Float
	'opponentSwitchSuccessPercentageTele' : 1.5, #Float
	'scaleSuccessPercentageAuto' : 1.5, #Float
	'scaleSuccessPercentageTele' : 1.5,
	'allianceSwitchFailPercentageAuto' : 1.5, #Float
	'allianceSwitchFailPercentageTele' : 1.5, #Float
	'opponentSwitchFailPercentageTele' : 1.5, #Float
	'scaleFailPercentageAuto' : 1.5, #Float
	'scaleFailPercentageTele' : 1.5,
	'predictedSeed' : 1,
	'actualSeed' : 1,
	'numMatchesPlayed' : None,
	'lfmAvgNumGoodDecicions' : None,
	'lfmAvgAllaicneSwitchCubesTele' : None,
	'name' : None,
	'number' : None,
	'lfmAvgNumPyramidintakeTele' : None,
	'lfmAvgCubesSpilled' : None,
	'avgCubesSpilled' : None,
	'dysfunctionalPercentage' : 1.5,
	'avgAllianceSwitchTimeTele' : 1.5, #Float
	'avgOpponentSwitchTimeTele' : 1.5,
	'avgAllianceSwitchTimeAuto' : 1.5, #Float
	'lfmAvgAllianceSwitchTimeTele' : 1.5, #Float
	'lfmAvgOpponentSwitchTimeTele' : 1.5,
	'lfmAvgAllianceSwitchTimeAuto' : 1.5, #Float
	'avgScaleTimeAuto' : 1.5,
	'avgScaleTimeTele' : 1.5,
	'lfmAvgScaleTimeAuto' : 1.5,
	'lfmAvgScaleTimeTele' : 1.5,
	'predictedTotalNumRPs' : 1.5,
	'pitAvgRampTime' : 1.5,
	'pitAvgDriveTime' : 1.5,
}

for thing in var3:
	db.child('Teams').child(thing.key()).child('calculatedData').set(teamCalc)

for timd in var1:
	if timd.key().split('Q')[0] != 'None':
		db.child('TeamInMatchDatas').child(str(timd.key())).child('teamNumber').set(int(timd.key().split('Q')[0]))
		db.child('TeamInMatchDatas').child(str(timd.key())).child('matchNumber').set(int(timd.key().split('Q')[1]))

teams = db.child('Teams').get().val().keys()
for team in teams:
	print(db.child('Teams').child(str(team)).child('number').get().val())
	db.child('Teams').child(str(team)).child('number').get().val()
	print(str(team))


#comp.updateTeamsAndMatchesFromFirebase()
#comp.updateTIMDsFromFirebase()
#print(calc.su.getTIMDsForMatch((calc.su.getMatchForNumber(104))))
#print(calc.getPointsEarnedOnScaleForAllianceAuto(calc.su.getMatchForNumber(104), False))
for timd in db.child('TeamInMatchDatas').get().val():
	print(timd)
	if 'None' not in str(timd):
		team = int(timd.split('Q')[0])
		match = int(timd.split('Q')[1])
		db.child('TeamInMatchDatas').child(timd).child('teamNumber').set(team)
		db.child('TeamInMatchDatas').child(timd).child('matchNumber').set(match)

teamCalc = {
	'avgNumOpponentPlatformIntakeAuto' : None,
	'avgOpponentSwitchCubesAuto' : None,
	'avgScaleTimeAuto' : 1.5,
	'avgScaleTimeTele' : 1.5,
	'avgAllianceTimeAuto' : None,
	'avgAllianceTimeTele' : None,
	'avgOpponentTimeTele' : None,
	'lfmAvgNumOpponentPlatformIntakeAuto' : None,
	'lfmAvgOpponentSwitchCubesAuto' : None,
	'lfmAvgScaleTimeAuto' : 1.5,
	'lfmAvgScaleTimeTele' : 1.5,
	'lfmAvgAllianceSwitchTimeAuto' : 1.5,
	'lfmAvgAllianceSwitchTimeTele' : 1.5,
	'lfmAvgOpponentSwitchTimeTele' : 1.5,
	'RScoreDefense' : 1.5,
	'RScoreSpeed' : 1.5,
	'RScoreAgility' : 1.5,
	'RScoreDrivingAbility' : 1.5,
	'firstPickAbility' : 1.5, #Float
	'secondPickAbility' : 1.5, #Float
	'disabledPercentage' : 1.5, #Float
	'incapacitatedPercentage' : 1.5, #Float
	'avgNumOpponentPlatformIntakeAuto' : None, #Float
	'avgNumAlliancePlatformIntakeAuto' : 1.5, #Float
	'avgNumGroundPyramidIntakeAuto' : 1.5, #Float
	'avgNumElevatedPyramidIntakeAuto' : 1.5, #Float
	'avgNumCubesFumbledAuto' : 1.5, #Float
	'avgNumCubesFumbledTele' : 1.5, #Float
	'avgNumGroundPyramidIntakeTele' : 1.5, #Float
	'avgNumElevatedPyramidIntakeTele' : 1.5, #Float
	'avgNumOpponentPlatformIntakeTele' : 1.5, #Float
	'avgNumAlliancePlatformIntakeTele' : 1.5, #Float
	'avgNumGroundIntakeTele' : 1.5, #Float
	'avgNumGroundPortalIntakeTele' : 1.5, #Float
	'avgNumHumanPortalIntakeTele' : 1.5, #Float
	'avgNumExchangeInputTele' : 1.5, #Float'
	'avgNumReturnIntakeTele' : 1.5, #Float
	'avgCubesSpilledAuto' : 1.5, #Float
	'avgCubesSpilledTele' : 1.5, #Float
	'avgCubesPlacedInScaleAuto' : 1.5, #Float
	'avgCubesPlacedInScaleTele' : 1.5, #Float
	'avgOpponentSwitchCubesAuto' : None, #Float
	'avgOpponentSwitchCubesTele' : 1.5, #Float
	'avgAllianceSwitchCubesAuto' : 1.5, #Float
	'avgAllianceSwitchCubesTele' : 1.5, #Float
	'avgNumGoodDecisions' : 1.5, #Float
	'avgNumBadDecisions' : 1.5, #Float
	'avgClimbTime' : 1.5, #Float
	'avgAgility' : 1.5, #Float
	'avgSpeed' : 1.5, #Float
	'avgDefense' : 1.5, #Float
	'avgDrivingAbility' : 1.5, #Float
	'lfmAvgNumOpponentPlatformIntakeAuto' : None, #Float
	'lfmAvgNumAlliancePlatformIntakeAuto' : 1.5, #Float
	'lfmAvgNumGroundPyramidIntakeAuto' : 1.5, #Float
	'lfmAvgNumElevatedPyramidIntakeAuto' : 1.5, #Float
	'lfmAvgNumElevatedPyramidIntakeTele' : 1.5, #Float
	'lfmAvgNumCubesFumbledAuto' : 1.5, #Float
	'lfmAvgNumCubesFumbledTele' : 1.5, #Float
	'lfmAvgNumOpponentPlatformIntakeTele' : 1.5, #Float
	'lfmAvgNumAlliancePlatformIntakeTele' : 1.5, #Float
	'lfmAvgNumGroundIntakeTele' : 1.5, #Float
	'lfmAvgNumGroundPortalIntakeTele' : 1.5, #Float
	'lfmAvgNumHumanPortalIntakeTele' : 1.5, #Float
	'lfmAvgNumExchangeInputTele' : 1.5, #Float
	'lfmAvgNumReturnIntakeTele' : 1.5, #Float
	'lfmAvgNumGoodDecisions' : 1.5, #Float
	'lfmAvgNumBadDecisions' : 1.5, #Float
	'lfmAvgCubesSpilledAuto' : 1.5, #Float
	'lfmAvgCubesSpilledTele' : 1.5, #Float
	'lfmAvgCubesPlacedInScaleAuto' : 1.5, #Float
	'lfmAvgCubesPlacedInScaleTele' : 1.5, #Float
	'lfmAvgOpponentSwitchCubesAuto' : None, #Float
	'lfmAvgOpponentSwitchCubesTele' : 1.5, #Float
	'lfmAvgAllianceSwitchCubesAuto' : 1.5, #Float
	'lfmAvgAllianceSwitchCubesTele' : 1.5, #Float
	'lfmAvgSpeed' : 1.5, #Float
	'lfmAvgDefense' : 1.5, #Float
	'lfmAvgAgility' : 1.5, #Float
	'lfmAvgDrivingAbility' : 1.5, #Float
	'totalNumGoodDecisions' : 1, #Int
	'totalNumBadDecisions' : 1, #Int
	'totalNumParks' : 1, #Int
	'totalNumRobotsLifted' : 1, #Int
	'totalNumRobotLiftAttempts' : 1, #Int
	'totalNumRobotsGroundLifted' : 1, #Int
	'totalNumRobotGroundLiftAttempts' : 1, #Int
	'numSuccessfulClimbs' : 1, #Int
	'predictedClimb' : 1.5, #Float CHANGED
	'climbPercentage' : 1.5, #Float
	'predictedNumAllianceSwitchCubesAuto' : 1.5, #Int CHANGED
	'predictedNumScaleCubesAuto' : 1.5, #Float CHANGED
	'actualNumRPs' : 1.5, #Float
	'predictedNumRPs' : 1.5, #Float
	'autoRunPercentage' : 1.5, #Float
	'switchFailPercentageAuto' : None, #Float
	'scaleSuccessPercentageAuto' : 1.5, #Float
	'switchFailPercentageTele' : None, #Float
	'scaleSuccessPercentageTele' : 1.5, #Float
	'canScoreBothSwitchSidesAuto' : True, #Bool
	'allianceSwitchSuccessPercentageAuto' : 1.5, #Float
	'allianceSwitchSuccessPercentageTele' : 1.5, #Float
	'opponentSwitchSuccessPercentageTele' : 1.5, #Float
	'scaleSuccessPercentageAuto' : 1.5, #Float
	'scaleSuccessPercentageTele' : 1.5,
	'allianceSwitchFailPercentageAuto' : 1.5, #Float
	'allianceSwitchFailPercentageTele' : 1.5, #Float
	'opponentSwitchFailPercentageTele' : 1.5, #Float
	'scaleFailPercentageAuto' : 1.5, #Float
	'scaleFailPercentageTele' : 1.5,
	'predictedSeed' : 1,
	'actualSeed' : 1,
	'numMatchesPlayed' : None,
	'lfmAvgNumGoodDecicions' : None,
	'lfmAvgAllaicneSwitchCubesTele' : None,
	'name' : None,
	'number' : None,
	'lfmAvgNumPyramidintakeTele' : None,
	'lfmAvgCubesSpilled' : None,
	'avgCubesSpilled' : None,
	'dysfunctionalPercentage' : 1.5,
	'avgAllianceSwitchTimeTele' : 1.5, #Float
	'avgOpponentSwitchTimeTele' : 1.5,
	'avgAllianceSwitchTimeAuto' : 1.5, #Float
	'lfmAvgAllianceSwitchTimeTele' : 1.5, #Float
	'lfmAvgOpponentSwitchTimeTele' : 1.5,
	'lfmAvgAllianceSwitchTimeAuto' : 1.5, #Float
	'avgScaleTimeAuto' : 1.5,
	'avgScaleTimeTele' : 1.5,
	'lfmAvgScaleTimeAuto' : 1.5,
	'lfmAvgScaleTimeTele' : 1.5,
	'predictedTotalNumRPs' : 1.5,
	'pitAvgRampTime' : 1.5,
	'pitAvgDriveTime' : 1.5,
}

db.child('Teams').child(180).child('calculatedData').set(teamCalc)
'''
rps = {team['team_key'] : team['extra_stats'][0] for team in TBAC.makeEventRankingsRequest()}
print(sorted(rps.keys(), key = lambda t: rps[t]))
		