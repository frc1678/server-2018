import utils
import firebaseCommunicator

#Creates classes with keys which correspond to the data points collected and calculated by our scouting system

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

	def updateTIMDsFromFirebase(self):
		self.TIMDs = utils.makeTIMDsFromDicts(self.PBC.getPythonObjectForFirebaseDataAtLocation('TeamInMatchDatas'))

	def updateCurrentMatchFromFirebase(self):
		self.currentMatchNum = self.PBC.firebase.child('currentMatchNum').get().val()

class CalculatedTeamData(object):
	'''c'''
	def __init__(self, **args):
		#initializes actual calculated team data
		super(CalculatedTeamData, self).__init__()
		self.firstPickAbility = None #Float
		self.secondPickAbility = None #Float 
		self.disabledPercentage = None #Float
		self.incapacitatedPercentage = None #Float
		self.dysfunctionalPercentage = None #Float
		self.numMatchesPlayed = None #Int
		self.avgNumRobotsLifted = None #Float
		self.avgNumCubesPlacedAuto = None #Float
		self.avgNumCubesPlacedTele = None #Float
		self.avgNumAlliancePlatformIntakeAuto = None #Float
		self.avgNumAlliancePlatformIntakeTele = None #Float
		self.avgNumOpponentPlatformIntakeTele = None #Float
		self.avgNumCubesFumbledAuto = None #Float
		self.avgNumCubesFumbledTele = None #Float
		self.avgNumElevatedPyramidIntakeAuto = None #Float
		self.avgNumElevatedPyramidIntakeTele = None #Float
		self.avgNumGroundPyramidIntakeAuto = None #Float
		self.avgNumGroundPyramidIntakeTele = None #Float
		self.avgNumGroundIntakeTele = None #Float
		self.avgNumGroundPortalIntakeTele = None #Float
		self.avgNumHumanPortalIntakeTele = None #Float
		self.avgNumExchangeInputTele = None #Float
		self.avgNumReturnIntakeTele = None #Float
		self.avgNumGoodDecisions = None #Float
		self.avgNumBadDecisions = None #Float
		self.avgCubesSpilledAuto = None #Float
		self.avgCubesSpilledTele = None #Float
		self.avgCubesPlacedInScaleAuto = None #Float
		self.avgCubesPlacedInScaleTele = None #Float
		self.avgAllianceSwitchCubesAuto = None #Float
		self.avgAllianceSwitchCubesTele = None #Float
		self.avgOpponentSwitchCubesTele = None #Float
		self.avgScaleTimeAuto = None #Float
		self.avgScaleTimeTele = None #Float
		self.avgTimeToOwnAllianceSwitchAuto = None #Float
		self.avgTimeToOwnScaleAuto = None #Float
		self.avgAllianceSwitchTimeAuto = None #Float
		self.avgAllianceSwitchTimeTele = None #Float
		self.avgOpponentSwitchTimeTele = None #Float
		self.avgScaleCubesBy100s = None #Float
		self.avgScaleCubesBy110s = None #Float
		self.avgAllVaultTime = None #Float
		self.avgClimbTime = None #Float
		self.avgAgility = None #Float
		self.avgSpeed = None #Float
		self.avgDefense = None #Float
		self.avgDrivingAbility = None #Float
		self.lfmAvgNumRobotsLifted = None #Float
		self.lfmAvgNumCubesPlacedAuto = None #Float
		self.lfmAvgNumCubesPlacedTele = None #Float
		self.lfmAvgNumAlliancePlatformIntakeAuto = None #Float
		self.lfmAvgNumAlliancePlatformIntakeTele = None #Float
		self.lfmAvgNumOpponentPlatformIntakeTele = None #Float
		self.lfmAvgNumCubesFumbledAuto = None #Float
		self.lfmAvgNumCubesFumbledTele = None #Float
		self.lfmAvgNumElevatedPyramidIntakeAuto = None #Float
		self.lfmAvgNumElevatedPyramidIntakeTele = None #Float
		self.lfmAvgNumGroundPyramidIntakeAuto = None #Float
		self.lfmAvgNumGroundPyramidIntakeTele = None #Float
		self.lfmAvgNumGroundIntakeTele = None #Float
		self.lfmAvgNumGroundPortalIntakeTele = None #Float
		self.lfmAvgNumHumanPortalIntakeTele = None #Float
		self.lfmAvgNumExchangeInputTele = None #Float
		self.lfmAvgNumReturnIntakeTele = None #Float
		self.lfmAvgNumGoodDecisions = None #Float
		self.lfmAvgNumBadDecisions = None #Float
		self.lfmAvgCubesSpilledAuto = None #Float
		self.lfmAvgCubesSpilledTele = None #Float
		self.lfmAvgCubesPlacedInScaleAuto = None #Float
		self.lfmAvgCubesPlacedInScaleTele = None #Float
		self.lfmAvgAllianceSwitchCubesAuto = None #Float
		self.lfmAvgAllianceSwitchCubesTele = None #Float
		self.lfmAvgOpponentSwitchCubesTele = None #Float
		self.lfmAvgScaleTimeAuto = None #Float
		self.lfmAvgScaleTimeTele = None #Float
		self.lfmAvgAllianceSwitchTimeAuto = None #Float
		self.lfmAvgAllianceSwitchTimeTele = None #Float
		self.lfmAvgOpponentSwitchTimeTele = None #Float
		self.lfmMaxScaleCubes = None #Int
		self.lfmMaxExchangeCubes = None #Int
		self.lfmAutoRunPercentage = None #Float
		self.lfmIncapacitatedPercentage = None #Float
		self.lfmDisabledPercentage = None #Float
		self.lfmDysfunctionalPercentage = None #Float
		self.lfmAvgTotalCubesPlaced = None #Float
		self.lfmSoloClimbPercentage = None #Float
		self.lfmAssistedClimbPercentage = None #Float
		self.lfmActiveLiftClimbPercentage = None #Float
		self.lfmActiveNoClimbLiftClimbPercentage = None #Float
		self.lfmActiveAssistClimbPercentage = None #Float
		self.lfmAvgScaleCubesBy100s = None #Float
		self.lfmAvgScaleCubesBy110s = None #Float
		self.lfmAvgAllVaultTime = None #Float
		self.lfmAvgClimbTime = None #Float
		self.lfmAvgSpeed = None #Float
		self.lfmAvgDefense = None #Float
		self.lfmAvgAgility = None #Float
		self.lfmAvgDrivingAbility = None #Float
		self.totalNumGoodDecisions = None #Int
		self.totalNumBadDecisions = None #Int
		self.totalNumParks = None #Int
		self.totalNumRobotsLifted = None #Int
		self.totalNumRobotLiftAttempts = None #Int
		self.totalNumRobotsGroundLifted = None #Int
		self.totalNumRobotGroundLiftAttempts = None #Int
		self.totalNumHighLayerScaleCubes = None #Int
		self.totalSuperNotes = None #List of String
		self.avgTotalCubesPlaced = None #Int
		self.numSuccessfulClimbs = None #Int
		self.predictedClimb = None #Float
		self.climbPercentage = None #Float
		self.soloClimbPercentage = None #Float
		self.activeAssistClimbPercentage = None #Float
		self.activeLiftClimbPercentage = None #Float
		self.activeNoClimbLiftClimbPercentage = None #Float
		self.assistedClimbPercentage = None #Float
		self.parkPercentage = None
		self.predictedSeed = None #Int
		self.actualSeed = None #Int
		self.predictedNumAllianceSwitchCubesAuto = None #Float
		self.predictedNumScaleCubesAuto = None #Float
		self.predictedPark = None #Float
		self.predictedNumRPs = None #Float
		self.predictedTotalNumRPs = None #Float
		self.totalNumRPs = None #Int
		self.actualNumRPs = None #Float
		self.autoRunPercentage = None #Float
		self.allianceSwitchSuccessPercentageAuto = None #Float
		self.allianceSwitchSuccessPercentageTele = None #Float
		self.opponentSwitchSuccessPercentageTele = None #Float
		self.scaleSuccessPercentageAuto = None #Float
		self.scaleSuccessPercentageTele = None #Float
		self.allianceSwitchFailPercentageAuto = None #Float
		self.allianceSwitchFailPercentageTele = None #Float
		self.opponentSwitchFailPercentageTele = None #Float
		self.scaleFailPercentageAuto = None #Float
		self.scaleFailPercentageTele = None #Float
		self.canScoreBothSwitchSidesAuto = None #Bool
		self.canPlaceHighLayerCube = None #Bool
		self.didThreeExchangeInputPercentage = None #Float
		self.percentSuccessOppositeSwitchSideAuto = None #Float
		self.canGroundIntake = None #Bool
		self.teleopExchangeAbility = None #Float
		self.teleopScaleAbility = None #Float
		self.teleopAllianceSwitchAbility = None #Float
		self.teleopOpponentSwitchAbility = None #Float
		self.vaultTimeScore = None #Float
		self.pitAvgDriveTime = None #Float
		self.pitAvgRampTime = None #Float
		self.maxScaleCubes = None #Int
		self.maxExchangeCubes = None #Int
		self.avgSwitchOwnership = None #Int
		self.lfmAvgSwitchOwnership = None #Int
		self.RScoreDefense = None #Float
		self.RScoreSpeed = None #Float
		self.RScoreAgility = None #Float
		self.RScoreDrivingAbility = None #Float
		self.__dict__.update(args) #DON'T DELETE THIS FOR ANY CLASS

class Team(object):
	'''FRC Team Object'''
	def __init__(self, **args):
		#initializes variables for each team
		super(Team, self).__init__()
		self.name = None #String
		self.number = None #Int
		self.calculatedData = CalculatedTeamData()
		self.pitSelectedImage = None #String
		self.pitAllImageURLs = [] #String
		self.pitAvailableWeight = None #Int
		self.pitDriveTrain = None #String
		self.pitImageKeys = [] #String
		self.pitSEALsNotes = None #String
		self.pitProgrammingLanguage = None #String
		self.pitClimberType = None #String
		self.pitRobotWidth = None #String
		self.pitRobotLength = None #String
		self.pitDriveTime = [] #List
		self.pitRampTime = [] #List
		self.pitDriveTimeOutcome = [] #List
		self.pitRampTimeOutcome = [] #List
		self.pitHasCamera = None #Bool
		self.pitWheelDiameter = None #String
		self.pitCanDoPIDOnDriveTrain = None #Bool
		self.pitHasGyro = None #Bool
		self.pitHasEncodersOnBothSides = None #Bool
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
		self.redPredictedPark = None #Float
		self.bluePredictedPark = None #Float
		self.redWinChance = None #Float
		self.blueWinChance = None #Float
		self.redLevitateProbability = None #Float
		self.blueLevitateProbability = None #Float
		self.redTeleopExchangeAbility = None #Float
		self.blueTeleopExchangeAbility = None #Float
		self.redPredictedFaceTheBoss = None #Float
		self.bluePredictedFaceTheBoss = None #Float
		self.__dict__.update(args)


class Match(object):
	'''An FRC Match Object'''
	def __init__(self, **args):
		#initializes match object
		super(Match, self).__init__()
		self.number = None #Int
		self.calculatedData = CalculatedMatchData()
		self.redAllianceTeamNumbers = None #Ints in a list
		self.blueAllianceTeamNumbers = None #Ints in a list
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
		self.numOpponentSwitchSuccessTele = None #Int
		self.numOpponentSwitchFailedTele = None #Int
		self.numScaleSuccessAuto = None #Int
		self.numScaleFailedAuto = None #Int
		self.numScaleSuccessTele = None #Int
		self.numScaleFailedTele = None #Int
		self.numCubesScaleAt100s = None #Int
		self.numCubesScaleAt110s = None #Int
		self.avgVaultTime = None #Float
		self.switchOwnership = None #Int
		self.climbTime = None #Float
		self.didClimb = None #Bool
		self.avgAllianceSwitchTimeAuto = None #Float
		self.avgAllianceSwitchTimeTele = None #Float
		self.avgOpponentSwitchTimeTele = None #Float
		self.avgScaleTimeAuto = None #Float
		self.avgScaleTimeTele = None #Float
		self.numOpponentPlatformIntakeTele = None #Int
		self.numAlliancePlatformIntakeAuto = None #Int
		self.numAlliancePlatformIntakeTele = None #Int
		self.numCubesPlacedAuto = None #Int
		self.numCubesPlacedTele = None #Int
		self.totalCubesPlaced = None #Int
		self.numClimbAttempts = None #Int
		self.isDysfunctional = None #Bool
		self.drivingAbility = None #Float
		self.didConflictWithAuto = None #Bool
		self.didThreeExchangeInput = None #Bool
		self.numRobotsLifted = None #Int
		self.timeToOwnAllianceSwitchAuto = None #Float
		self.timeToOwnScaleAuto = None #Float
		self.canScoreOppositeSwitchAuto = None #Bool
		self.switchIsOpposite = None #Bool
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
				'status' : None, #String opponentOwned or balanced
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
		self.climb = [ {
			'passiveClimb' : {
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
			},
			'assistedClimb' : {
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
			},
			'activeLift' : {
				'didSucceed' : None, #Bool 
				'didClimb' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None, #Float
				'partnerLiftType' : None, #String
				'didFailToLift' : None, #Bool
				'numRobotsLifted' : None #Int
			},
			'soloClimb' : {
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
			}
		} ]		
		self.didGetDisabled = None #Bool
		self.didGetIncapacitated = None #Bool
		self.didMakeAutoRun = None #Bool
		self.didPark = None #Bool
		self.numGoodDecisions = None #Int
		self.numBadDecisions = None #Int
		self.lastExchangeCubeTime = None #Float
		self.alliancePlatformIntakeAuto = {
			0 : None, #Bool
			1 : None, #Bool 
			2 : None, #Bool
			3 : None, #Bool
			4 : None, #Bool 
			5 : None, #Bool
			}
		self.alliancePlatformIntakeTele = {
			0 : None, #Bool
			1 : None, #Bool 
			2 : None, #Bool
			3 : None, #Bool
			4 : None, #Bool 
			5 : None, #Bool
			}
		self.opponentPlatformIntakeTele = {
			0 : None, #Bool
			1 : None, #Bool 
			2 : None, #Bool
			3 : None, #Bool
			4 : None, #Bool 
			5 : None, #Bool
			}
		self.vault = [ 
			{
				'time' : None, #Float
				'cubes' : None #Int
			} 
		]
		self.numCubesFumbledAuto = None #Int
		self.numCubesFumbledTele = None #Int
		self.numExchangeInput = None #Int
		self.numGroundIntakeTele = None #Int
		self.numGroundPortalIntakeTele = None #Int
		self.numHumanPortalIntakeTele = None #Int
		self.numGroundPyramidIntakeAuto = None
		self.numGroundPyramidIntakeTele = None
		self.numElevatedPyramidIntakeAuto = None
		self.numElevatedPyramidIntakeTele = None 
		self.totalNumScaleFoul = None #Int
		self.numReturnIntake = None #Int
		self.numSpilledCubesAuto = None #Int
		self.numSpilledCubesTele = None #Int
		self.rankAgility = None #Int
		self.rankDefense = None #Int
		self.rankSpeed = None #Int
		self.startingPosition = None #String 'left' 'right' or 'center'
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
