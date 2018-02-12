#Last Updated: 1/15/17
import pyrebase
import random
import time
import DataModel
import firebaseCommunicator

#Makes a lot of random data and sets data on firebase for testing

class CalculatedTeamInMatchData(object):
	'''docstring for CalculatedTeamInMatchData'''
	def __init__(self, **args):
		#initializer for random CalculatedTIMDs
		super(CalculatedTeamInMatchData, self).__init__()
		self.numRPs = random.randint(0, 4)
		self.numAllianceSwitchSuccessAuto = random.randint(0, 6)
		self.numAllianceSwitchSuccessTele = random.randint(0, 12)
		self.numAllianceSwitchFailedAuto = random.randint(0, 3)
		self.numAllianceSwitchFailedTele = random.randint(0, 8)
		self.numOpponentSwitchSuccessAuto = random.randint(0, 6)
		self.numOpponentSwitchSuccessTele = random.randint(0, 12)
		self.numOpponentSwitchFailedAuto = random.randint(0, 3)
		self.numOpponentSwitchFailedTele = random.randint(0, 8)
		self.numAlliancePlatformIntakeAuto = random.randint(0, 3)
		self.numAlliancePlatformIntakeTele = random.randint(0, 8)
		self.numOpponentPlatformIntakeAuto = random.randint(0, 3)
		self.numOpponentPlatFormIntakeTele = random.randint(0, 8)
		self.numScaleSuccessAuto = random.randint(0, 2)
		self.numScaleFailedAuto = random.randint(0, 2)
		self.numScaleSuccessTele = random.randint(0, 12)
		self.numScaleFailedTele = random.randint(0, 8)
		self.climbTime = float(random.randint(0, 30))
		self.avgAllianceSwitchTimeTele = float(random.randint(0, 135))
		self.avgOpponentSwitchTimeTele = float(random.randint(0, 135))
		self.avgScaleTimeAuto = float(random.randint(0, 15))
		self.avgAllianceSwitchTimeAuto = float(random.randint(0, 15))
		self.avgOpponentSwitchTimeAuto = float(random.randint(0, 15))
		self.avgScaleTimeTele =  float(random.randint(0, 135))
		self.numCubesPlacedAuto = random.randint(0, 3)
		self.numCubesPlacedTele = random.randint(0, 20)
		self.numClimbAttempts = random.randint(0, 4)
		self.isDysfunctional = bool(random.randint(0, 1))
		self.drivingAbility = float(random.randint(0, 100))
		self.didConflictWithAuto = bool(random,randint(0, 1))

class TeamInMatchData(object):
	'''An FRC TeamInMatchData Object'''
	def __init__(self, **args):
		#initializer for random TIMDs
		super(TeamInMatchData, self).__init__()
		self.calculatedData = CalculatedTeamInMatchData()
		self.teamNumber = random.randint(1, 9999)
		self.matchNumber = random.randint(0, 99)
		self.scoutName = random.choice('a b c d e f g h i j k l m n o p q r'.split())
		self.superNotes = random.choice(['y u so bad', 'spinbot!', 'ok team', 'they have the good good', 'juicy', 'battery fell out'])
		self.allianceSwitchAttemptAuto = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]
		self.allianceSwitchAttemptTele = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]
		self.climb = [ {
			'passiveLift' : {
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(105, 120)),
				'endTime' : float(random.randint(120, 135))
			},
			'assistedLift' : {
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(105, 120)),
				'endTime' : float(random.randint(120, 135))
			},
			'activeLift' : {
				'didSucceed' : bool(random.randint(0, 1)),
				'didClimb' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(105, 120)),
				'endTime' : float(random.randint(120, 135)),
				'partnerLiftType' : random.choice(['passiveLift', 'assistedLift']),
				'didFailToLift' : bool(random.randint(0, 1)),
				'numRobotsLifted' : random.randint(1, 3)
			},
			'climb' : {
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(105, 120)),
				'endTime' : float(random.randint(120, 135))
			}
		} ]		
		self.didGetDisabled = bool(random.randint(0, 1))
		self.didGetIncapacitated = bool(random.randint(0, 1))
		self.didMakeAutoRun = bool(random.randint(0, 1))
		self.didPark = bool(random.randint(0, 1))
		self.numGoodDecisions = random.randint(0, 24)
		self.numBadDecisions = random.randint(0, 24)
		self.alliancePlatformIntakeAuto = [random.randint(4, 7), random.randint(0, 3)]
		self.alliancePlatformIntakeTele = [random.randint(0, 3), random.randint(4, 7), random.randint(0, 3), random.randint(4, 7)]
		self.numCubesFumbledAuto = random.randint(0, 3)
		self.numCubesFumbledTele = random.randint(0, 16)
		self.numExchangeInput = random.randint(0, 9)
		self.numGroundIntakeTele = random.randint(0, 10)
		self.numGroundPortalIntakeTele = random.randint(0, 12)
		self.numHumanPortalIntakeTele = random.randint(0, 12)
		self.numGroundPyramidIntakeAuto = random.randint(0, 4)
		self.numGroundPyramidIntakeTele = random.randint(0, 10)
		self.numElevatedPyramidIntakeAuto = random.randint(0, 4)
		self.numElevatedPyramidIntakeTele = random.randint(0, 5)
		self.opponentPlatformIntakeAuto = [random.randint(4, 7), random.randint(0, 3)]
		self.opponentPlatformIntakeTele = [random.randint(0, 3), random.randint(4, 7), random.randint(0, 3), random.randint(4, 7)]
		self.numReturnIntake = random.randint(0, 5)
		self.numSpilledCubesAuto = random.randint(0, 2)
		self.numSpilledCubesTele = random.randint(0, 8)
		self.rankAgility = random.randint(0, 4)
		self.rankDefense = random.randint(0, 4)
		self.rankSpeed = random.randint(0, 4)
		self.startingPosition = random.choice(['left', 'center', 'right'])
		self.opponentSwitchAttemptTele = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]
		self.scaleAttemptAuto = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]
		self.scaleAttemptTele = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]

class TempTeamInMatchDatas(object):
	'''TempTIMDs For Testing Calcs'''
	def __init__(self, **args):
		#initializer for random TempTIMDs
		super(TempTeamInMatchDatas, self).__init__()
		self.scoutName = random.choice('a b c d e f g h i j k l m n o p q r'.split())
		self.allianceSwitchAttemptAuto = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]
		self.allianceSwitchAttemptTele = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]
		self.climb = [ {
			'passiveLift' : {
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(105, 120)),
				'endTime' : float(random.randint(120, 135))
			},
			'assistedLift' : {
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(105, 120)),
				'endTime' : float(random.randint(120, 135))
			},
			'activeLift' : {
				'didSucceed' : bool(random.randint(0, 1)),
				'didClimb' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(105, 120)),
				'endTime' : float(random.randint(120, 135)),
				'partnerLiftType' : random.choice(['passiveLift', 'assistedLift']),
				'didFailToLift' : bool(random.randint(0, 1)),
				'numRobotsLifted' : random.randint(1, 3)
			},
			'climb' : {
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(105, 120)),
				'endTime' : float(random.randint(120, 135))
			}
		} ]		
		self.didGetDisabled = bool(random.randint(0, 1))
		self.didGetIncapacitated = bool(random.randint(0, 1))
		self.didMakeAutoRun = bool(random.randint(0, 1))
		self.didPark = bool(random.randint(0, 1))
		self.alliancePlatformIntakeAuto = [bool(random.getrandbits(1)) for x in range(6)]
		self.alliancePlatformIntakeTele = [bool(random.getrandbits(1)) for x in range(6)]
		self.numCubesFumbledAuto = random.randint(0, 3)
		self.numCubesFumbledTele = random.randint(0, 16)
		self.numExchangeInput = random.randint(0, 9)
		self.numGroundIntakeTele = random.randint(0, 10)
		self.numGroundPortalIntakeTele = random.randint(0, 12)
		self.numHumanPortalIntakeTele = random.randint(0, 12)
		self.numGroundPyramidIntakeAuto = random.randint(0, 4)
		self.numGroundPyramidIntakeTele = random.randint(0, 10)
		self.numElevatedPyramidIntakeAuto = random.randint(0, 4)
		self.numElevatedPyramidIntakeTele = random.randint(0, 5)
		self.opponentPlatformIntakeAuto = [bool(random.getrandbits(1)) for x in range(6)]
		self.opponentPlatformIntakeTele = [bool(random.getrandbits(1)) for x in range(6)]
		self.numReturnIntake = random.randint(0, 5)
		self.numSpilledCubesAuto = random.randint(0, 2)
		self.numSpilledCubesTele = random.randint(0, 8)
		self.startingPosition = random.choice(['left', 'center', 'right'])
		self.opponentSwitchAttemptTele = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]
		self.scaleAttemptAuto = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]
		self.scaleAttemptTele = [
			{
				'didSucceed' : bool(random.randint(0, 1)),
				'startTime' : float(random.randint(0, 50)),
				'endTime' : float(random.randint(50, 100)),
				'status' : random.choice(['ownedRed', 'balanced', 'ownedBlue']),
				'layer' : random.randint(0, 4)
			} for num in range(1, 10)
		]

class Match(object):
	'''An FRC Match Object'''
	def __init__(self, **args):
		#initializer for random matches
		super(Match, self).__init__()
		numbers = [str(random.randint(1, 9999))] * 50
		self.number = random.randint(100, 9999)
		self.calculatedData = CalculatedMatchData()
		self.redAllianceTeamNumbers = [random.choice[numbers]] * 3
		self.blueAllianceTeamNumbers = [random.choice[numbers]] * 3
		self.blueCubesForPowerup = {
			'Boost' : random.randint(0, 3),
			'Force' : random.randint(0, 3),
			'Levitate' : random.randint(0, 3)
		}
		self.blueCubesInVaultFinal = {
			'Boost' : random.randint(0, 3),
			'Force' : random.randint(0, 3),
			'Levitate' : random.randint(0, 3)
		}
		self.blueDidAutoQuest = bool(random.randint(0, 1))
		self.blueDidFaceBoss = bool(random.randint(0, 1))
		self.blueSwitch = {
			'left' : 'blue',
			'right' : 'red'
		}
		self.redCubesForPowerup = {
			'Boost' : random.randint(0, 3),
			'Force' : random.randint(0, 3),
			'Levitate' : random.randint(0, 3)
		}
		self.redCubesInVaultFinal = {
			'Boost' : random.randint(0, 3),
			'Force' : random.randint(0, 3),
			'Levitate' : random.randint(0, 3)
		}
		self.redDidAutoQuest = bool(random.randint(0, 1))
		self.redDidFaceBoss = bool(random.randint(0, 1))
		self.redSwitch = {
			'left' : 'blue',
			'right' : 'red'
		}
		self.scale = {
			'left' : 'blue',
			'right' : 'red'
		}
		self.redScore = random.randint(0, 999)
		self.blueScore = random.randint(0, 999)
		self.foulPointsGainedRed = random.randint(0, 199)
		self.foulPointsGainedBlue = random.randint(0, 199)

class CalculatedMatchData(object):
	'''docstring for CalculatedMatchData'''
	def __init__(self, **args):
		#initializer for random match data
		super(CalculatedMatchData, self).__init__()
		self.predictedBlueScore = random.randint(0, 199)
		self.predictedRedScore = random.randint(0, 199)
		self.predictedBlueRPs = random.randint(0, 4)
		self.actualBlueRPs = random.randint(0, 4)
		self.predictedRedRPs = random.randint(0, 4)
		self.actualRedRPs = random.randint(0, 4)
		self.predictedBlueAutoQuest = bool(random.randint(0, 1))
		self.predictedRedAutoQuest = bool(random.randint(0, 1))
		self.redWinChance = float(random.randint(0, 100))
		self.blueWinChance = 100 - self.redWinChance

config = {
	'apiKey': 'mykey',
	'authDomain': 'into-the-firebase-and-flames.firebaseapp.com',
	'storageBucket': 'into-the-firebase-and-flames.appspot.com',
	'databaseURL': 'into-the-firebase-and-flames.firebaseio.com/'
	# 'authDomain': '1678-scouting-2016.firebaseapp.com',
	# 'storageBucket': '1678-scouting-2016.appspot.com',
	# 'databaseURL': 'https://1678-scouting-2016.firebaseio.com/'
	# 'authDomain': '1678-dev-2016.firebaseapp.com',
	# 'storageBucket': '1678-dev-2016.appspot.com',
	# 'databaseURL': 'https://1678-dev-2016.firebaseio.com/'
}
pbc = firebaseCommunicator.PyrebaseCommunicator()
app = pyrebase.initialize_app(config)
fb = pbc.firebase
testScouts = 'a b c d e f g h i j k l m n o p q r'.split()
testScoutNums = {}
for i in range(len(testScouts)):
	testScoutNums[testScouts[i]] = i + 1
cm = 1
mnum = 1
newTempTIMDs = TempTeamInMatchDatas()
TIMDs = fb.child('TeamInMatchDatas').get().val()
#First removes all tempTIMDs from current firebase
print('Removing old tempTIMDs...')
fb.child('TempTeamInMatchDatas').remove()
print('Successfully removed all tempTIMDs\nCreating and uploading random data...')
#Uploads the random data
for TIMD in TIMDs:
	name = fb.child('TeamInMatchDatas').child(TIMD).get().key()
	scoutsPerMatch = random.randint(1, 3)
	for num in range(0, scoutsPerMatch):
		randScout = random.choice(testScouts)
		fb.child('TempTeamInMatchDatas').child((str(name) + '-' + str(testScoutNums[randScout]))).set(newTempTIMDs.__dict__)
	print('Created and uploaded a tempTIMD- ' + str(name) + ' | ' + str(mnum))
	break
	mnum += 1
time.sleep(1)
print('Done.')
