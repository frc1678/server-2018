#Last Updated: 10/12/17
import firebaseCommunicator
import utils

#creates classes with keys which correspond to the data points collected and calculated by our scouting

class Competition(object):
	'''docstring for Competition'''
	def __init__(self, PBC):
		super(Competition, self).__init__()
		self.code = ''
		self.teams = []
		self.matches = []
		self.TIMDs = []
		self.PBC = PBC
		self.currentMatchNum = 0
	def updateTeamsAndMatchesFromFirebase(self):
		self.teams = utils.makeTeamsFromDicts(self.PBC.getPythonObjectForFirebaseDataAtLocation('Teams'))
		self.matches = utils.makeMatchesFromDicts(self.PBC.getPythonObjectForFirebaseDataAtLocation('Matches'))
		self.teams = utils.makeTeamsFromDicts(self.PBC.getPythonObjectForFirebaseDataAtLocation('Teams'))
		self.matches = utils.makeMatchesFromDicts(self.PBC.getPythonObjectForFirebaseDataAtLocation('Matches'))

	def updateTIMDsFromFirebase(self):
		self.TIMDs = utils.makeTIMDsFromDicts(self.PBC.getPythonObjectForFirebaseDataAtLocation('TeamInMatchDatas'))

class CalculatedTeamData(object):
	'''c'''
	def __init__(self, **args):
		#initializes actual calculated team data
		super(CalculatedTeamData, self).__init__()
		self.firstPickAbility = None #Float
		self.secondPickAbility = None #Float
		self.disabledPercentage = None #Float
		self.incapacitatedPercentage = None #Float
		self.avgNumOpponentPlatformIntakeAuto = None #Int
		self.avgNumAlliancePlatformIntakeAuto = None #Int CHANGED
		self.avgNumGroundPyramidIntakeAuto = None #Int
		self.avgNumElevatedPyramidIntakeAuto = None #Int
		self.avgNumCubesFumbledAuto = None #Int
		self.avgNumCubesFumbledTele = None #Int
		self.avgNumGroundPyramidIntakeTele = None #Int
		self.avgNumElevatedPyramidIntakeTele = None #Int
		self.avgNumOpponentPlatformIntakeTele = None #Int
		self.avgNumAlliancePlatformIntakeTele = None #Int
		self.avgNumGroundIntakeTele = None #Int
		self.avgNumGroundPortalIntakeTele = None
		self.avgNumHumanPortalIntakeTele = None
		self.avgNumExchangeInputTele = None #Int
		self.avgNumReturnIntakeTele = None #Int Add Schema Change
		self.avgCubesSpilledAuto = None #Int
		self.avgCubesSpilledTele = None #Int
		self.avgCubesPlacedInScaleAuto = None #Float
		self.avgCubesPlacedInSwitchAuto = None #Float
		self.avgCubesPlacedInScaleTele = None #Float
		self.avgCubesPlacedInSwitchTele = None #Float
		self.avgNumGoodDecicions = None #Float
		self.avgNumBadDecisions = None #Float
		self.avgClimbTime = None #Float
		self.avgAgility = None #Float
		self.avgSpeed = None #Float
		self.avgDefense = None #Float
		self.avgDrivingAbility = None #Float
		self.lfmAvgNumOpponentPlatformIntakeAuto = None #Float
		self.lfmAvgNumAlliancePlatformIntakeAuto = None #Float
		self.lfmAvgNumGroundPyramidIntakeAuto = None #Float
		self.lfmAvgNumGroundPyramidIntakeTele = None #Float
		self.lfmAvgNumElevatedPyramidIntakeAuto = None #Float
		self.lfmAvgNumElevatedPyramidIntakeTele = None #Float
		self.lfmAvgNumCubesFumbledAuto = None #Float
		self.lfmAvgNumCubesFumbledTele = None #Float
		self.lfmAvgNumOpponentPlatformIntakeTele = None #Float
		self.lfmAvgNumAlliancePlatformIntakeTele = None #Float
		self.lfmAvgNumGroundIntakeTele = None #Float
		self.lfmAvgNumGroundPortalIntakeTele = None #Float
		self.lfmAvgNumHumanPortalIntakeTele = None #Float
		self.lfmAvgNumExchangeInputTele = None #Float
		self.lfmAvgNumReturnIntakeTele = None #Float
		self.lfmAvgNumGoodDecisions = None #Float
		self.lfmAvgNumBadDecisions = None #Float
		self.lfmAvgCubesSpilledAuto = None #Float
		self.lfmAvgCubesSpilledTele = None #Float
		self.lfmAvgSpeed = None #Float
		self.lfmAvgDefense = None #Float
		self.lfmAvgAgility = None #Float
		self.lfmAvgDrivingAbility = None #Float
		self.predictedClimb = None #Float CHANGED
		self.climbPercentage = None #Float
		self.predictedNumAllianceSwitchCubesAuto = None #Int CHANGED
		self.predictedNumScaleCubesAuto = None #Int CHANGED
		self.actualNumRPs = None #Float
		self.predictedNumRPs = None #Float
		self.autoRunPercentage = None #Float
		self.switchFailPercentageAuto = None #Float
		self.scaleFailPercentageAuto = None #Float
		self.switchFailPercentageTele = None #Float
		self.scaleFailPercentageTele = None #Float
		self.canScoreBothSwitchSidesAuto = None #Bool
		self.__dict__.update(args) #DON'T DELETE THIS FOR ANY CLASS

class Team(object):
	'''FRC Team Object'''
	def __init__(self, **args):
		#initializes variables for each team
		super(Team, self).__init__()
		self.name = None #String
		self.number = None #Int
		self.calculatedData = CalculatedTeamData()
		self.numMatchesPlayed = None #Int
		self.pitSelectedImageName = None #String
		self.pitAllImageURLs = {} #String
		self.pitAvailableWeight = None #Int
		self.pitDriveTrain = None #String
		self.pitImageKeys = {} #String CHANGED
		self.pitDidDemonstrateCheesecakePotential = None #Bool
		self.pitSEALsNotes = None #String
		self.pitProgrammingLanguage = None #String
		self.pitClimberType = None #String
		self.pitMaxHeight = None #Probably Int, maybe float
		self.__dict__.update(args)

class CalculatedMatchData(object):
	'''docstring for CalculatedMatchData'''
	def __init__(self, **args):
		#initializes actual calculated match data
		super(CalculatedMatchData, self).__init__()
		self.predictedBlueScore = None #Float
		self.predictedRedScore = None #Float
		self.predictedBlueRPs = None #Float
		self.actualBlueRPs = None #Int
		self.predictedRedRPs = None #Float
		self.actualRedRPs = None #Int
		self.predictedBlueAutoQuest = None #Bool
		self.predictedRedAutoQuest = None #Bool
		self.redWinChance = None #Float
		self.blueWinChance = None #Float
		self.__dict__.update(args)


class Match(object):
	'''An FRC Match Object'''
	def __init__(self, **args):
		#initializes match object
		super(Match, self).__init__()
		self.number = None #Int
		self.calculatedData = CalculatedMatchData()
		self.redAllianceTeamNumbers = None #Strings in a list
		self.blueAllianceTeamNumbers = None #Strings in a list
		self.blueCubesForPowerup = {
			'Boost' : None, #Int
			'Force' : None, #Int
			'Levitate' : None #Int
		}
		self.blueCubesInVaultFinal = {
			'Boost' : None, #Int
			'Force' : None, #Int
			'Levitate' : None #Int
		}
		self.blueDidAutoQuest = None #Bool
		self.blueDidFaceBoss = None #Bool
		self.blueSwitch = {
			'left' : None, #String
			'right' : None #String
		}
		self.redCubesForPowerup = {
			'Boost' : None, #Int
			'Force' : None, #Int
			'Levitate' : None #Int
		}
		self.redCubesInVaultFinal = {
			'Boost' : None, #Int
			'Force' : None, #Int
			'Levitate' : None #Int
		}
		self.redDidAutoQuest = None #Bool
		self.redDidFaceBoss = None #Bool
		self.redSwitch = {
			'left' : None, #String
			'right' : None #String
		}
		self.scale = {
			'left' : None, #String
			'right' : None #String
		}
		self.redScore = None #Int
		self.blueScore = None #Int
		self.foulPointsGainedRed = None #Int
		self.foulPointsGainedBlue = None #Int
		self.__dict__.update(args)

class CalculatedTeamInMatchData(object):
	'''docstring for CalculatedTeamInMatchData'''
	def __init__(self, **args):
		#initializes actual CalculatedTIMDs
		super(CalculatedTeamInMatchData, self).__init__()
		self.numRPs = None #Int
		self.numAllianceSwitchSuccessAuto = None #Int
		self.numAllianceSwitchSuccessTele = None #Int
		self.numAllianceSwitchFailedAuto = None #Int
		self.numAllianceSwitchFailedTele = None #Int
		self.numOpponentSwitchSuccessAuto = None #Int
		self.numOpponentSwitchSuccessTele = None #Int
		self.numOpponentSwitchFailedAuto = None #Int
		self.numOpponentSwitchFailedTele = None #Int
		self.numScaleSuccessAuto = None #Int
		self.numScaleFailedAuto = None #Int
		self.numScaleSuccessTele = None #numReturnIntake
		self.numScaleFailedTele = None #Int
		self.climbTime = None #Float
		self.avgAllianceSwitchTimeTele = None #Float
		self.avgOpponentSwitchTimeTele = None #Float
		self.avgScaleTimeAuto = None #Float
		self.avgAllianceSwitchTimeAuto = None #Float
		self.avgOpponentSwitchTimeAuto = None #Float
		self.avgScaleTimeTele = None #Float
		self.numCubesPlacedAuto = None #Int
		self.numCubesPlacedTele = None #Int
		self.numClimbAttempts = None #Int
		self.isDysfunctional = None #Bool
		self.drivingAbility = None #Float probably
		self.didConflictWithAuto = None #Bool
		self.__dict__.update(args)

class TeamInMatchData(object):
	'''An FRC TeamInMatchData Object'''
	def __init__(self, **args):
		#initializes actual TIMDs
		super(TeamInMatchData, self).__init__()
		self.calculatedData = CalculatedTeamInMatchData()
		self.teamNumber = None #Int 
		self.matchNumber = None #Int
		self.scoutName = None #String
		self.superNotes = None #String
		self.allianceSwitchAttemptAuto = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None, #Float
				'status' : None, #String
				'layer' : None #Int
			}
		]
		self.allianceSwitchAttemptTele = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None, #Float
				'status' : None, #String
				'layer' : None #Int
			}
		]
		self.climb = {
			'passiveLift' : {
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
			},
			'assistedLift' : {
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
			},
			'activeLift' : {
				'didSucceed' : None, #Bool 
				'startTime' : None, #Float
				'endTime' : None, #Float
				'partnerLiftType' : None, #String
				'didFailToLift' : None, #Bool
				'numRobotsLifted' : None #Int
			},
			'climb' : {
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
			}
		}		
		self.didGetDisabled = None #Bool
		self.didGetIncapacitated = None #Bool
		self.didMakeAutoRun = None #Bool
		self.didPark = None #Bool
		self.numBadDecisions = None #Int
		self.numAlliancePlatformIntakeAuto = [] #List of Int
		self.numAlliancePlatformIntakeTele = [] #List of Int
		self.numCubesFumbledAuto = None #Int
		self.numCubesFumbledTele = None #Int
		self.numExchangeInput = None #Int
		self.numGoodDecisions = None #Int
		self.numGroundIntakeTele = None #Int
		self.numGroundPortalIntakeTele = None #Int
		self.numHumanPortalIntakeTele = None #Int
		self.numGroundPyramidIntakeAuto = None
		self.numGroundPyramidIntakeTele = None
		self.numElevatedPyramidIntakeAuto = None
		self.numElevatedPyramidIntakeTele = None 
		self.numOpponentPlatformIntakeAuto = [] #List of Int
		self.numOpponentPlatformIntakeTele = [] #List of Int
		self.numReturnIntake = None #Int
		self.numSpilledCubesAuto = None #Int
		self.numSpilledCubesTele = None #Int
		self.rankAgility = None #Int
		self.rankDefense = None #Int
		self.rankSpeed = None #Int
		self.startingPosition = None #String 'left' 'right' or 'center' CHANGED
		self.opponentSwitchAttemptTele = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None, #Float
				'status' : None, #String
				'layer' : None #Int
			}
		]
		self.scaleAttemptAuto = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None, #Float
				'status' : None, #String
				'layer' : None #Int
			}
		]
		self.scaleAttemptTele = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None, #Float
				'status' : None, #String
				'layer' : None #Int
			}
		]
		self.__dict__.update(args)
