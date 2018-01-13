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
		self.avgNumRedPlatformIntakeAuto = None #Int
		self.avgNumBluePlatformIntakeAuto = None #Int CHANGED
		self.avgNumPyramidIntakeAuto = None #Int
		self.avgNumCubesFumbledAuto = None #Int
		self.avgNumCubesFumbledTele = None #Int
		self.avgNumPyramidIntakeTele = None #Int
		self.avgNumRedPlatformIntakeTele = None #Int
		self.avgNumBluePlatformIntakeTele = None #Int
		self.avgNumGroundIntakeTele = None #Int
		self.avgNumPortalIntakeTele = { #CHANGED
			'groundIntake' : None, #Float
			'humanIntake' : None #Float
		} 
		self.avgNumExchangeInputTele = None #Int
		self.avgNumReturnIntakeTele = None #Int
		self.avgCubesSpilledAuto = None #Int
		self.avgCubesSpilledTele = None #Int
		self.avgAgility = None #Float
		self.avgSpeed = None #Float
		self.avgDefense = None #Float
		self.avgStacking = None #Float CHANGED
		self.avgDrivingAbility = None #Float
		self.lfmAvgNumRedPlatformIntakeAuto = None #Float
		self.lfmAvgNumBluePlatformIntakeAuto = None #Float
		self.lfmAvgNumPyramidIntakeAuto = None #Float
		self.lfmAvgNumPyramidIntakeTele = None #Float
		self.lfmAvgNumCubesFumbledAuto = None #Float
		self.lfmAvgNumCubesFumbledTele = None #Float
		self.lfmAvgNumRedPlatformIntakeTele = None #Float
		self.lfmAvgNumBluePlatformIntakeTele = None #Float
		self.lfmAvgNumGroundIntakeTele = None #Float
		self.lfmAvgNumPortalIntakeTele = {
			'groundIntake' : None, #Float
			'humanIntake' : None #Float
		} 
		self.lfmAvgNumExchangeInputTele = None #Float
		self.lfmAvgNumReturnIntakeTele = None #Float
		self.lfmAvgCubesSpilledAuto = None #Float
		self.lfmAvgCubesSpilledTele = None #Float
		self.lfmAvgSpeed = None #Float
		self.lfmAvgDefense = None #Float
		self.lfmAvgAgility = None #Float
		self.lfmAvgDrivingAbility = None #Float
		self.lfmAvgStacking = None #Float CHANGED
		self.predictedClimb = None #Float CHANGED
		self.predictedNumBlueSwitchCubesAuto = None #Int CHANGED
		self.predictedNumRedSwitchCubesAuto = None #Int CHANGED
		self.predictedNumScaleCubesAuto = None #Int CHANGED
		self.actualNumRPs = None #Float
		self.predictedNumRPs = None #Float
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
		self.pitSEALSnotes = None #String
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
		self.numRedSwitchSuccessAuto = None #Int
		self.numRedSwitchSuccessTele = None #Int
		self.numRedSwitchFailedAuto = None #Int
		self.numRedSwitchFailedTele = None #Int
		self.numBlueSwitchSuccessAuto = None #Int
		self.numBlueSwitchSuccessTele = None #Int
		self.numBlueSwitchFailedAuto = None #Int
		self.numBlueSwitchFailedTele = None #Int
		self.numScaleSuccessAuto = None #Int
		self.numScaleFailedAuto = None #Int
		self.numScaleSuccessTele = None #Int
		self.numScaleFailedTele = None #Int
		self.avgRedSwitchTimeTele = None #Float
		self.avgBlueSwitchTimeTele = None #Float
		self.avgScaleTimeAuto = None #Float
		self.avgRedSwitchTimeAuto = None #Float
		self.avgBlueSwitchTimeAuto = None #Float
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
		self.blueSwitchAttemptAuto = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
			}
		]
		self.blueSwitchAttemptTele = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
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
				'liftingPartner' : {
					'liftType' : None
				}
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
		self.numBluePlatformIntakeAuto = [] #List of Int
		self.numBluePlatformIntakeTele = [] #List of Int
		self.numCubesFumbledAuto = None #Int
		self.numCubesFumbledTele = None #Int
		self.numExchangeInput = None #Int
		self.numGoodDecisions = None #Int
		self.numGroundIntakeTele = None #Int
		self.numPortalIntakeTele = { 
			'groundIntake' : None, #Int
			'humanIntake' : None #Int
		}
		self.numPyramidIntakeAuto = {
			'groundLevel' : None, #Int
			'elevatedLevel' : None #Int
		}
		self.numPyramidIntakeTele = {
			'groundLevel' : None, #Int
			'elevatedLevel' : None #Int
		}
		self.numRedPlatformIntakeAuto = [] #List of Int
		self.numRedPlatformIntakeTele = [] #List of Int
		self.numReturnIntake = None #Int
		self.numSpilledCubesAuto = None #Int
		self.numSpilledCubesTele = None #Int
		self.rankAgility = None #Int
		self.rankDefense = None #Int
		self.rankSpeed = None #Int
		self.rankStacking = None #Int
		self.startingPosition = None #String 'left' 'right' or 'center' CHANGED
		self.redSwitchAttemptAuto = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
			}
		]
		self.redSwitchAttemptTele = [
			{
				'didSucceed' : None, #Bool
				'startTime' : None, #Float
				'endTime' : None #Float
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
