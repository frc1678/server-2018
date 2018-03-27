#Last Updated: 2/11/18
import utils
import DataModel
import pdb
import traceback
import firebaseCommunicator
PBC = firebaseCommunicator.PyrebaseCommunicator()

def mapFuncForCalcAvgsForTeam(team, func, **calcDatas):		
	[team.calculatedData.__dict__.update({k : func(dataFunc)}) for k, dataFunc in calcDatas.items()]

def firstCalculationDict(team, calc):
    cd = team.calculatedData
    mapFuncForCalcAvgsForTeam(team, lambda f: calc.getAverageForDataFunctionForTeam(team, f), 
        disabledPercentage = lambda tm: tm.didGetDisabled,
        incapacitatedPercentage = lambda tm: tm.didGetIncapacitated,
        dysfunctionalPercentage = lambda tm: tm.calculatedData.isDysfunctional,
        avgNumAlliancePlatformIntakeAuto = lambda tm: tm.calculatedData.numAlliancePlatformIntakeAuto,
        avgNumAlliancePlatformIntakeTele = lambda tm: tm.calculatedData.numAlliancePlatformIntakeTele,
        avgNumOpponentPlatformIntakeTele = lambda tm: tm.calculatedData.numOpponentPlatformIntakeTele,
        avgNumCubesFumbledAuto = lambda tm: tm.numCubesFumbledAuto,
        avgNumCubesFumbledTele = lambda tm: tm.numCubesFumbledTele,
        avgNumGroundPyramidIntakeAuto = lambda tm: tm.numGroundPyramidIntakeAuto,
        avgNumGroundPyramidIntakeTele = lambda tm: tm.numGroundPyramidIntakeTele,
        avgNumElevatedPyramidIntakeAuto = lambda tm: tm.numElevatedPyramidIntakeAuto,
        avgNumElevatedPyramidIntakeTele = lambda tm: tm.numElevatedPyramidIntakeTele,
        avgNumGroundIntakeTele = lambda tm: tm.numGroundIntakeTele,
        avgNumGroundPortalIntakeTele = lambda tm: tm.numGroundPortalIntakeTele,
        avgNumHumanPortalIntakeTele = lambda tm: tm.numHumanPortalIntakeTele,
        avgNumExchangeInputTele = lambda tm: tm.numExchangeInput,
        avgNumBadDecisions = lambda tm: tm.numBadDecisions, 
        avgNumGoodDecisions = lambda tm: tm.numGoodDecisions,
        avgNumReturnIntakeTele = lambda tm: tm.numReturnIntake,
        avgCubesSpilledAuto = lambda tm: tm.numSpilledCubesAuto,
        avgCubesSpilledTele = lambda tm: tm.numSpilledCubesTele,
        avgCubesPlacedInScaleAuto = lambda tm: tm.calculatedData.numScaleSuccessAuto,   
        avgCubesPlacedInScaleTele = lambda tm: tm.calculatedData.numScaleSuccessTele,
        avgAllianceSwitchCubesAuto = lambda tm: tm.calculatedData.numAllianceSwitchSuccessAuto, 
        avgAllianceSwitchCubesTele = lambda tm: tm.calculatedData.numAllianceSwitchSuccessTele,
        avgOpponentSwitchCubesTele = lambda tm: tm.calculatedData.numOpponentSwitchSuccessTele,
        avgScaleTimeAuto = lambda tm: tm.calculatedData.avgScaleTimeAuto,
        avgScaleTimeTele = lambda tm: tm.calculatedData.avgScaleTimeTele,
        avgAllianceSwitchTimeAuto = lambda tm: tm.calculatedData.avgAllianceSwitchTimeAuto,
        avgAllianceSwitchTimeTele = lambda tm: tm.calculatedData.avgAllianceSwitchTimeTele,
        avgOpponentSwitchTimeTele = lambda tm: tm.calculatedData.avgOpponentSwitchTimeTele,
        avgClimbTime = lambda tm: tm.calculatedData.climbTime,
        avgAgility = lambda tm: tm.rankAgility,    
        avgDefense = lambda tm: tm.rankDefense, 
        avgSpeed = lambda tm: tm.rankSpeed,
        avgDrivingAbility = lambda tm: tm.calculatedData.drivingAbility,
        actualNumRPs = lambda tm: tm.calculatedData.numRPs,
        autoRunPercentage = lambda tm: tm.didMakeAutoRun, 
        climbPercentage = lambda tm: tm.calculatedData.didClimb,
        didThreeExchangeInputPercentage = lambda tm: tm.calculatedData.didThreeExchangeInput,
        avgNumRobotsLifted = lambda tm: tm.calculatedData.numRobotsLifted,
        avgTimeToOwnAllianceSwitchAuto = lambda tm: tm.calculatedData.timeToOwnAllianceSwitchAuto,
        avgTimeToOwnScaleAuto = lambda tm: tm.calculatedData.timeToOwnScaleAuto,
        avgNumCubesPlacedAuto = lambda tm: tm.calculatedData.numCubesPlacedAuto,
        avgNumCubesPlacedTele = lambda tm: tm.calculatedData.numCubesPlacedTele,
        )
    mapFuncForCalcAvgsForTeam(team, lambda f: calc.getRecentAverageForDataFunctionForTeam(team, f),
        lfmDisabledPercentage = lambda tm: tm.didGetDisabled,
        lfmIncapacitatedPercentage = lambda tm: tm.didGetIncapacitated,
        lfmDysfunctionalPercentage = lambda tm: tm.calculatedData.isDysfunctional,
        lfmAvgNumAlliancePlatformIntakeAuto = lambda tm: tm.calculatedData.numAlliancePlatformIntakeAuto,
        lfmAvgNumAlliancePlatformIntakeTele = lambda tm: tm.calculatedData.numAlliancePlatformIntakeTele,
        lfmAvgNumOpponentPlatformIntakeTele = lambda tm: tm.calculatedData.numOpponentPlatformIntakeTele,
        lfmAvgNumCubesFumbledAuto = lambda tm: tm.numCubesFumbledAuto,
        lfmAvgNumCubesFumbledTele = lambda tm: tm.numCubesFumbledTele,
        lfmAvgNumBadDecisions = lambda tm: tm.numBadDecisions, 
        lfmAvgNumExchangeInputTele = lambda tm: tm.numExchangeInput,
        lfmAvgNumGoodDecisions = lambda tm: tm.numGoodDecisions,
        lfmAvgNumGroundIntakeTele = lambda tm: tm.numGroundIntakeTele,
        lfmAvgNumGroundPortalIntakeTele = lambda tm: tm.numGroundPortalIntakeTele,
        lfmAvgNumHumanPortalIntakeTele = lambda tm: tm.numHumanPortalIntakeTele,
        lfmAvgNumGroundPyramidIntakeAuto = lambda tm: tm.numGroundPyramidIntakeAuto,
        lfmAvgNumGroundPyramidIntakeTele = lambda tm: tm.numGroundPyramidIntakeTele,
        lfmAvgNumElevatedPyramidIntakeAuto = lambda tm: tm.numElevatedPyramidIntakeAuto,
        lfmAvgNumElevatedPyramidIntakeTele = lambda tm: tm.numElevatedPyramidIntakeTele,
        lfmAvgNumReturnIntakeTele = lambda tm: tm.numReturnIntake,
        lfmAvgCubesSpilledAuto = lambda tm: tm.numSpilledCubesAuto,
        lfmAvgCubesSpilledTele = lambda tm: tm.numSpilledCubesTele,
        lfmAvgAgility = lambda tm: tm.rankAgility,
        lfmAvgDefense = lambda tm: tm.rankDefense, 
        lfmAvgSpeed = lambda tm: tm.rankSpeed,
        lfmAvgDrivingAbility = lambda tm: tm.calculatedData.drivingAbility,
        lfmActualNumRPs = lambda tm: tm.calculatedData.numRPs,
        lfmAvgAllianceSwitchCubesAuto = lambda tm: tm.calculatedData.numAllianceSwitchSuccessAuto,
        lfmAvgAllianceSwitchCubesTele = lambda tm: tm.calculatedData.numAllianceSwitchSuccessTele,
        lfmAvgOpponentSwitchCubesTele = lambda tm: tm.calculatedData.numOpponentSwitchSuccessTele,
        lfmAvgCubesPlacedInScaleAuto = lambda tm: tm.calculatedData.numScaleSuccessAuto,
        lfmAvgCubesPlacedInScaleTele = lambda tm: tm.calculatedData.numScaleSuccessTele,
        lfmAvgScaleTimeAuto = lambda tm: tm.calculatedData.avgScaleTimeAuto,
        lfmAvgScaleTimeTele = lambda tm: tm.calculatedData.avgScaleTimeTele,
        lfmAvgAllianceSwitchTimeAuto = lambda tm: tm.calculatedData.avgAllianceSwitchTimeAuto,
        lfmAvgAllianceSwitchTimeTele = lambda tm: tm.calculatedData.avgAllianceSwitchTimeTele,
        lfmAvgOpponentSwitchTimeTele = lambda tm: tm.calculatedData.avgOpponentSwitchTimeTele,
        lfmAvgNumRobotsLifted = lambda tm: tm.calculatedData.numRobotsLifted,
        lfmAvgNumCubesPlacedAuto = lambda tm: tm.calculatedData.numCubesPlacedAuto,
        lfmAvgNumCubesPlacedTele = lambda tm: tm.calculatedData.numCubesPlacedTele,
        lfmAutoRunPercentage = lambda tm: tm.didMakeAutoRun,
        lfmAvgClimbTime = lambda tm: tm.calculatedData.climbTime,
        )
    mapFuncForCalcAvgsForTeam(team, lambda f: calc.getSumForDataFunctionForTeam(team, f),
        totalNumGoodDecisions = lambda tm: tm.numGoodDecisions,
        totalNumBadDecisions = lambda tm: tm.numBadDecisions,
        totalNumParks = lambda tm: tm.didPark,
        numSuccessfulClimbs = lambda tm: tm.calculatedData.didClimb,
        totalNumRobotsLifted = lambda tm: tm.calculatedData.numRobotsLifted,
        )
    cd.predictedPark = calc.predictedParkForTeam(team)
    cd.soloClimbPercentage = calc.getPercentageForClimbType(team, 'soloClimb', False)
    cd.assistedClimbPercentage = calc.getPercentageForClimbType(team, 'assistedClimb', False)
    cd.activeLiftClimbPercentage = calc.getPercentageForActiveClimbType(team, True, 'passive', False)
    cd.activeNoClimbLiftClimbPercentage = calc.getPercentageForActiveClimbType(team, False, 'passive', False)
    cd.activeAssistClimbPercentage = calc.getPercentageForActiveClimbType(team, True, 'assisted', False)
    cd.lfmSoloClimbPercentage = calc.getPercentageForClimbType(team, 'soloClimb', True)
    cd.lfmAssistedClimbPercentage = calc.getPercentageForClimbType(team, 'assistedClimb', True)
    cd.lfmActiveLiftClimbPercentage = calc.getPercentageForActiveClimbType(team, True, 'passive', True)
    cd.lfmActiveNoClimbLiftClimbPercentage = calc.getPercentageForActiveClimbType(team, False, 'passive', True)
    cd.lfmActiveAssistClimbPercentage = calc.getPercentageForActiveClimbType(team, True, 'assisted', True)
    cd.allianceSwitchSuccessPercentageAuto = calc.getAllianceSwitchSuccessPercentageAuto(team)
    cd.allianceSwitchSuccessPercentageTele = calc.getAllianceSwitchSuccessPercentageTele(team)
    cd.opponentSwitchSuccessPercentageTele = calc.getOpponentSwitchSuccessPercentageTele(team)
    cd.scaleSuccessPercentageAuto = calc.getScaleSuccessPercentageAuto(team)
    cd.scaleSuccessPercentageTele = calc.getScaleSuccessPercentageTele(team)
    cd.allianceSwitchFailPercentageAuto = 1 - cd.allianceSwitchSuccessPercentageAuto
    cd.allianceSwitchFailPercentageTele = 1 - cd.allianceSwitchSuccessPercentageTele
    cd.opponentSwitchFailPercentageTele = 1 - cd.opponentSwitchSuccessPercentageTele
    cd.scaleFailPercentageAuto = 1 - cd.scaleSuccessPercentageAuto
    cd.scaleFailPercentageTele = 1 - cd.scaleSuccessPercentageTele
    cd.canScoreBothSwitchSidesAuto = calc.getCanScoreBothSwitchSidesAuto(team)
    cd.canPlaceHighLayerCube = calc.getCanPlaceHighLayerCube(team)
    cd.totalNumHighLayerScaleCubes = calc.getTotalNumHighLayerScaleCubes(team)
    cd.canGroundIntake = calc.getCanGroundIntake(team)
    cd.totalSuperNotes = calc.getTotalSuperNotes(team)
    cd.percentSuccessOppositeSwitchSideAuto = calc.getPercentSuccessOppositeSwitchSideAuto(team)
    cd.maxScaleCubes = calc.getMaxScaleCubes(team, False)
    cd.lfmMaxScaleCubes = calc.getMaxScaleCubes(team, True)
    cd.maxExchangeCubes = calc.getMaxExchangeCubes(team, False)
    cd.lfmMaxExchangeCubes = calc.getMaxExchangeCubes(team, True)
    cd.numMatchesPlayed = len(calc.su.getCompletedTIMDsForTeam(team))
    cd.parkPercentage = calc.parkPercentageForTeam(team)
    cd.totalCubesPlaced = calc.getTotalCubesPlaced(team, False)
    cd.lfmTotalCubesPlaced = calc.getTotalCubesPlaced(team, True)
    cd.autoRunPercentage = calc.autoRunBackup(team)

def Rscorecalcs(team, calc):
    cd = team.calculatedData
    cd.RScoreDefense = calc.cachedComp.defenseZScores[team.number]
    cd.RScoreSpeed = calc.cachedComp.speedZScores[team.number]
    cd.RScoreAgility = calc.cachedComp.agilityZScores[team.number]
    cd.RScoreDrivingAbility = calc.cachedComp.drivingAbilityZScores[team.number]

def secondCalculationDict(team, calc):
    cd = team.calculatedData
    cd.teleopScaleAbility = calc.getTeleopScaleAbilityForTeam(team)
    cd.teleopExchangeAbility = calc.getTeleopExchangeAbilityForTeam(team)
    cd.teleopAllianceSwitchAbility = calc.getTeleopAllianceSwitchAbilityForTeam(team)
    cd.teleopOpponentSwitchAbility = calc.getTeleopOpponentSwitchAbilityForTeam(team)
    cd.predictedTotalNumRPs = calc.predictedTotalNumRPsForTeam(team)
    cd.predictedNumRPs = calc.predictedNumRPsForTeam(team)
    try:
        cd.actualNumRPs = calc.getTeamRPsFromTBA(team)
        cd.actualSeed = calc.getTeamSeed(team)
    except KeyboardInterrupt:
        return
    except:
        if team in calc.cachedComp.actualSeedings:
            cd.actualSeed = calc.cachedComp.actualSeedings.index(team) + 1
            cd.actualNumRPs = calc.actualNumberOfRPs(team)
    if team in calc.cachedComp.teamsWithMatchesCompleted:
        cd.RScoreDrivingAbility = calc.cachedComp.drivingAbilityZScores[team.number]
        cd.predictedSeed = calc.cachedComp.predictedSeedings.index(team) + 1
    try:
        cd.firstPickAbility = calc.getFirstPickAbilityForTeam(team)
        cd.secondPickAbility = calc.getSecondPickAbilityForTeam(team)
    except:
        pass

def TIMDCalcDict(timd, calc):
    if (not calc.su.TIMCalculatedDataHasValues(timd.calculatedData)):
        timd.calculatedData = DataModel.CalculatedTeamInMatchData()
    team = calc.su.getTeamForNumber(timd.teamNumber)
    match = calc.su.getMatchForNumber(timd.matchNumber)
    c = timd.calculatedData
    c.numAllianceSwitchSuccessAuto = calc.getTotalAttemptsForValueListDicts(True, timd.allianceSwitchAttemptAuto)
    c.numAllianceSwitchSuccessTele = calc.getTotalAttemptsForValueListDicts(True, timd.allianceSwitchAttemptTele)
    c.numAllianceSwitchFailedAuto = calc.getTotalAttemptsForValueListDicts(False, timd.allianceSwitchAttemptAuto)
    c.numAllianceSwitchFailedTele = calc.getTotalAttemptsForValueListDicts(False, timd.allianceSwitchAttemptTele) 
    c.numOpponentSwitchSuccessTele = calc.getTotalAttemptsForValueListDicts(True, timd.opponentSwitchAttemptTele)
    c.numOpponentSwitchFailedTele = calc.getTotalAttemptsForValueListDicts(False, timd.opponentSwitchAttemptTele)
    c.numScaleSuccessAuto = calc.getTotalAttemptsForValueListDicts(True, timd.scaleAttemptAuto)
    c.numScaleSuccessTele = calc.getTotalAttemptsForValueListDicts(True, timd.scaleAttemptTele)
    c.numScaleFailedAuto = calc.getTotalAttemptsForValueListDicts(False, timd.scaleAttemptAuto)
    c.numScaleFailedTele = calc.getTotalAttemptsForValueListDicts(False, timd.scaleAttemptTele)
    c.climbTime = calc.getClimbTime(timd.climb)
    c.didClimb = calc.getDidClimb(timd.climb)
    c.avgAllianceSwitchTimeAuto = calc.getAvgSuccessTimeForListDicts(timd.allianceSwitchAttemptAuto)
    c.avgAllianceSwitchTimeTele = calc.getAvgSuccessTimeForListDicts(timd.allianceSwitchAttemptTele)
    c.avgOpponentSwitchTimeTele = calc.getAvgSuccessTimeForListDicts(timd.opponentSwitchAttemptTele)
    c.avgScaleTimeAuto = calc.getAvgSuccessTimeForListDicts(timd.scaleAttemptAuto)
    c.avgScaleTimeTele = calc.getAvgSuccessTimeForListDicts(timd.scaleAttemptTele)
    c.numAlliancePlatformIntakeAuto = calc.getTotalSuccessForListOfBools(timd.alliancePlatformIntakeAuto)
    c.numAlliancePlatformIntakeTele = calc.getTotalSuccessForListOfBools(timd.alliancePlatformIntakeTele)
    c.numOpponentPlatformIntakeTele = calc.getTotalSuccessForListOfBools(timd.opponentPlatformIntakeTele)
    c.numCubesPlacedAuto = calc.getTotalSuccessForListListDicts([timd.allianceSwitchAttemptAuto, timd.scaleAttemptAuto])
    c.numCubesPlacedTele = (calc.getTotalSuccessForListListDicts([timd.allianceSwitchAttemptTele, timd.opponentSwitchAttemptTele, timd.scaleAttemptTele])) + timd.numExchangeInput
    c.numClimbAttempts = calc.getClimbAttempts(timd.climb)
    c.drivingAbility = calc.drivingAbilityForTeam(team)
    c.didConflictWithAuto = calc.checkAutoForConflict()
    c.didThreeExchangeInput = calc.getDidThreeExchangeInput(timd)
    c.isDysfunctional = utils.convertFirebaseBoolean(timd.didGetDisabled + utils.convertFirebaseBoolean(timd.didGetIncapacitated))
    c.numRobotsLifted = calc.getNumRobotsLifted(timd)
    c.timeToOwnAllianceSwitchAuto = calc.getTimeToOwnAllianceSwitchAuto(timd)
    c.timeToOwnScaleAuto = calc.getTimeToOwnScaleAuto(timd)
    c.canScoreOppositeSwitchAuto = calc.getCanScoreOppositeSwitch(timd, team, match)
    c.switchIsOpposite = calc.getSwitchIsOpposite(timd, team, match)

def averageTeamDict(calc):
    a = calc.averageTeam
    mapFuncForCalcAvgsForTeam(calc.averageTeam, lambda f: calc.getAverageOfDataFunctionAcrossCompetition(f),
        avgNumBadDecisions = lambda t: t.calculatedData.avgNumBadDecisions, 
        avgNumCubesFumbledAuto = lambda t: t.calculatedData.avgNumCubesFumbledAuto,
        avgNumCubesFumbledTele = lambda t: t.calculatedData.avgNumCubesFumbledTele,
        avgNumExchangeInputTele = lambda t: t.calculatedData.avgNumExchangeInputTele,
        avgNumGoodDecisions = lambda t: t.calculatedData.avgNumGoodDecisions,
        avgNumGroundIntakeTele = lambda t: t.calculatedData.avgNumGroundIntakeTele,
        avgNumAlliancePlatformIntakeAuto = lambda t: t.calculatedData.avgNumAlliancePlatformIntakeAuto,
        avgNumAlliancePlatformIntakeTele = lambda t: t.calculatedData.avgNumAlliancePlatformIntakeTele,
        avgNumOpponentPlatformIntakeTele = lambda t: t.calculatedData.avgNumOpponentPlatformIntakeTele,
        avgNumGroundPortalIntakeTele = lambda t: t.calculatedData.avgNumGroundPortalIntakeTele,
        avgNumHumanPortalIntakeTele = lambda t: t.calculatedData.avgNumHumanPortalIntakeTele,
        avgNumGroundPyramidIntakeAuto = lambda t: t.calculatedData.avgNumGroundPyramidIntakeAuto,
        avgNumGroundPyramidIntakeTele = lambda t: t.calculatedData.avgNumGroundPyramidIntakeTele,
        avgNumElevatedPyramidIntakeAuto = lambda t: t.calculatedData.avgNumElevatedPyramidIntakeAuto,
        avgNumElevatedPyramidIntakeTele = lambda t: t.calculatedData.avgNumElevatedPyramidIntakeTele,
        avgNumReturnIntakeTele = lambda t: t.calculatedData.avgNumReturnIntakeTele,
        avgCubesSpilledAuto = lambda t: t.calculatedData.avgCubesSpilledAuto,
        avgCubesSpilledTele = lambda t: t.calculatedData.avgCubesSpilledTele,
        avgAgility = lambda t: t.calculatedData.avgAgility,
        avgDefense = lambda t: t.calculatedData.avgDefense, 
        avgSpeed = lambda t: t.calculatedData.avgSpeed,
        avgDrivingAbility = lambda t: t.calculatedData.avgDrivingAbility,
        actualNumRPs = lambda t: t.calculatedData.actualNumRPs,
        avgAllianceSwitchCubesAuto = lambda t: t.calculatedData.avgAllianceSwitchCubesAuto,
        avgAllianceSwitchCubesTele = lambda t: t.calculatedData.avgAllianceSwitchCubesTele,
        avgOpponentSwitchCubesTele = lambda t: t.calculatedData.avgOpponentSwitchCubesTele,
        avgCubesPlacedInScaleAuto = lambda t: t.calculatedData.avgCubesPlacedInScaleAuto,
        avgCubesPlacedInScaleTele = lambda t: t.calculatedData.avgCubesPlacedInScaleTele,
        avgClimbTime = lambda t: t.calculatedData.avgClimbTime,
        disabledPercentage = lambda t: t.calculatedData.disabledPercentage,
        incapacitatedPercentage = lambda t: t.calculatedData.incapacitatedPercentage,
        dysfunctionalPercentage = lambda t: t.calculatedData.dysfunctionalPercentage,
        autoRunPercentage = lambda t: t.calculatedData.autoRunPercentage,
        )

def matchDict(match, calc):
    if calc.su.matchIsCompleted(match):
        match.calculatedData.actualBlueRPs = calc.RPsGainedFromMatchForAlliance(False, match)
        match.calculatedData.actualRedRPs = calc.RPsGainedFromMatchForAlliance(True, match)
    match.calculatedData.bluePredictedPark = calc.predictedParkForAlliance(match, False)
    match.calculatedData.redPredictedPark = calc.predictedParkForAlliance(match, True)
    match.calculatedData.bluePredictedFaceTheBoss = calc.predictedFaceTheBoss(match, False)
    match.calculatedData.redPredictedFaceTheBoss = calc.predictedFaceTheBoss(match, True)
    match.calculatedData.predictedBlueAutoQuest = calc.predictedAutoQuestRP(match, False)
    match.calculatedData.predictedRedAutoQuest = calc.predictedAutoQuestRP(match, True)
    match.calculatedData.blueLevitateProbability = calc.levitateProbabilityForAlliance(match, False)
    match.calculatedData.redLevitateProbability = calc.levitateProbabilityForAlliance(match, True)
    match.calculatedData.predictedBlueScore = calc.getPredictedScoreForAlliance(match, False)
    match.calculatedData.predictedRedScore = calc.getPredictedScoreForAlliance(match, True)
    match.calculatedData.predictedBlueRPs = calc.predictedRPsForAlliance(match, False)
    match.calculatedData.predictedRedRPs = calc.predictedRPsForAlliance(match, True)
