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
        avgNumBadDecisions = lambda tm: tm.numBadDecisions, 
        avgNumCubesFumbledAuto = lambda tm: tm.numCubesFumbledAuto,
        avgNumCubesFumbledTele = lambda tm: tm.numCubesFumbledTele,
        avgNumExchangeInputTele = lambda tm: tm.numExchangeInput,
        avgNumGoodDecisions = lambda tm: tm.numGoodDecisions,
        avgNumGroundIntakeTele = lambda tm: tm.numGroundIntakeTele,
        avgNumAlliancePlatformIntakeAuto = lambda tm: tm.calculatedData.numAlliancePlatformIntakeAuto,
        avgNumAlliancePlatformIntakeTele = lambda tm: tm.calculatedData.numAlliancePlatformIntakeTele,
        avgNumOpponentPlatformIntakeTele = lambda tm: tm.calculatedData.numOpponentPlatformIntakeTele,
        avgNumGroundPortalIntakeTele = lambda tm: tm.numGroundPortalIntakeTele,
        avgNumHumanPortalIntakeTele = lambda tm: tm.numHumanPortalIntakeTele,
        avgNumGroundPyramidIntakeAuto = lambda tm: tm.numGroundPyramidIntakeAuto,
        avgNumGroundPyramidIntakeTele = lambda tm: tm.numGroundPyramidIntakeTele,
        avgNumElevatedPyramidIntakeAuto = lambda tm: tm.numElevatedPyramidIntakeAuto,
        avgNumElevatedPyramidIntakeTele = lambda tm: tm.numElevatedPyramidIntakeTele,
        avgNumReturnIntakeTele = lambda tm: tm.numReturnIntake,
        avgCubesSpilledAuto = lambda tm: tm.numSpilledCubesAuto,
        avgCubesSpilledTele = lambda tm: tm.numSpilledCubesTele,
        avgAgility = lambda tm: tm.rankAgility,    
        avgDefense = lambda tm: tm.rankDefense, 
        avgSpeed = lambda tm: tm.rankSpeed,
        avgDrivingAbility = lambda tm: tm.calculatedData.drivingAbility,
        actualNumRPs = lambda tm: tm.calculatedData.numRPs,
        avgAllianceSwitchCubesAuto = lambda tm: tm.calculatedData.numAllianceSwitchSuccessAuto, 
        avgAllianceSwitchCubesTele = lambda tm: tm.calculatedData.numAllianceSwitchSuccessTele,
        avgOpponentSwitchCubesTele = lambda tm: tm.calculatedData.numOpponentSwitchSuccessTele,
        avgCubesPlacedInScaleAuto = lambda tm: tm.calculatedData.numScaleSuccessAuto,   
        avgCubesPlacedInScaleTele = lambda tm: tm.calculatedData.numScaleSuccessTele,
        avgScaleTimeAuto = lambda tm: tm.calculatedData.avgScaleTimeAuto,
        avgScaleTimeTele = lambda tm: tm.calculatedData.avgScaleTimeTele,
        avgAllianceSwitchTimeAuto = lambda tm: tm.calculatedData.avgAllianceSwitchTimeAuto,
        avgAllianceSwitchTimeTele = lambda tm: tm.calculatedData.avgAllianceSwitchTimeTele,
        avgOpponentSwitchTimeTele = lambda tm: tm.calculatedData.avgOpponentSwitchTimeTele,
        avgClimbTime = lambda tm: tm.calculatedData.climbTime,
        disabledPercentage = lambda tm: tm.didGetDisabled,
        incapacitatedPercentage = lambda tm: tm.didGetIncapacitated,
        dysfunctionalPercentage = lambda tm: tm.calculatedData.isDysfunctional,
        autoRunPercentage = lambda tm: tm.didMakeAutoRun,
        climbPercentage = lambda tm: tm.calculatedData.didClimb,
        )
    mapFuncForCalcAvgsForTeam(team, lambda f: calc.getRecentAverageForDataFunctionForTeam(team, f),
        lfmAvgNumBadDecisions = lambda tm: tm.numBadDecisions, 
        lfmAvgNumCubesFumbledAuto = lambda tm: tm.numCubesFumbledAuto,
        lfmAvgNumCubesFumbledTele = lambda tm: tm.numCubesFumbledTele,
        lfmAvgNumExchangeInputTele = lambda tm: tm.numExchangeInput,
        lfmAvgNumGoodDecisions = lambda tm: tm.numGoodDecisions,
        lfmAvgNumGroundIntakeTele = lambda tm: tm.numGroundIntakeTele,
        lfmAvgNumAlliancePlatformIntakeAuto = lambda tm: tm.calculatedData.numAlliancePlatformIntakeAuto,
        lfmAvgNumAlliancePlatformIntakeTele = lambda tm: tm.calculatedData.numAlliancePlatformIntakeTele,
        lfmAvgNumOpponentPlatformIntakeTele = lambda tm: tm.calculatedData.numOpponentPlatformIntakeTele,
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
        )
    mapFuncForCalcAvgsForTeam(team, lambda f: calc.getSumForDataFunctionForTeam(team, f),
        totalNumGoodDecisions = lambda tm: tm.numGoodDecisions,
        totalNumBadDecisions = lambda tm: tm.numBadDecisions,
        totalNumParks = lambda tm: tm.didPark,
        numSuccessfulClimbs = lambda tm: tm.calculatedData.didClimb,
        )

def Rscorecalcs(team, calc):
    cd = team.calculatedData
    cd.RScoreDefense = calc.cachedComp.defenseZScores[team.number]
    cd.RScoreSpeed = calc.cachedComp.speedZScores[team.number]
    cd.RScoreAgility = calc.cachedComp.agilityZScores[team.number]
    cd.RScoreDrivingAbility = calc.cachedComp.drivingAbilityZScores[team.number]

def secondCalculationDict(team, calc):
    '''
    cd = team.calculatedData
    cd.predictedNumRPs = calc.predictedNumberOfRPs(team)
    cd.firstPickRotorBonusChance = calc.firstPickAllRotorsChance(team)
    try:
        cd.actualNumRPs = calc.getTeamRPsFromTBA(team)
        cd.actualSeed = calc.getTeamSeed(team)
    except KeyboardInterrupt:
        break
    except:
        if team in calc.cachedComp.actualSeedings:
            cd.actualSeed = calc.cachedComp.actualSeedings.index(team) + 1
            cd.actualNumRPs = calc.actualNumberOfRPs(team)
    if team in calc.cachedComp.teamsWithMatchesCompleted:
        cd.RScoreDrivingAbility = calc.cachedComp.drivingAbilityZScores[team.number]
        cd.predictedSeed = calc.cachedComp.predictedSeedings.index(team) + 1
    cd.firstPickAbility = calc.firstPickAbility(team)
    cd.allRotorsAbility = calc.allRotorsAbility(team)
    '''

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
    c.avgAllianceSwitchTimeAuto = calc.getAvgSuccessTimeForListDicts(timd.allianceSwitchAttemptAuto)
    c.avgAllianceSwitchTimeTele = calc.getAvgSuccessTimeForListDicts(timd.allianceSwitchAttemptTele)
    c.avgOpponentSwitchTimeTele = calc.getAvgSuccessTimeForListDicts(timd.opponentSwitchAttemptTele)
    c.avgScaleTimeAuto = calc.getAvgSuccessTimeForListDicts(timd.scaleAttemptAuto)
    c.avgScaleTimeTele = calc.getAvgSuccessTimeForListDicts(timd.scaleAttemptTele)
    c.numCubesPlacedAuto = calc.getTotalSuccessForListListDicts([timd.allianceSwitchAttemptAuto, timd.scaleAttemptAuto])
    c.numCubesPlacedTele = calc.getTotalSuccessForListListDicts([timd.allianceSwitchAttemptTele, timd.opponentSwitchAttemptTele, timd.scaleAttemptTele])
    c.numClimbAttempts = calc.getClimbAttempts(timd.climb)
    c.climbTime = calc.getClimbTime(timd.climb)
    c.drivingAbility = calc.getDrivingAbility()
    c.didConflictWithAuto = calc.checkAutoForConflict()
    c.isDysfunctional = utils.convertFirebaseBoolean(timd.didGetDisabled + utils.convertFirebaseBoolean(timd.didGetIncapacitated))
    c.numRPs = calc.RPsGainedFromMatchForAlliance(team.number in match.redAllianceTeamNumbers, match)
    
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
    '''
    if calc.su.matchIsCompleted(match):
        match.calculatedData.actualBlueRPs = calc.RPsGainedFromMatchForAlliance(True, match)
        match.calculatedData.actualRedRPs = calc.RPsGainedFromMatchForAlliance(False, match)
    match.calculatedData.predictedBlueScore = calc.predictedScoreForAllianceWithNumbers(match.blueAllianceTeamNumbers)
    match.calculatedData.predictedRedScore = calc.predictedScoreForAllianceWithNumbers(match.redAllianceTeamNumbers)
    match.calculatedData.sdPredictedBlueScore = calc.stdDevPredictedScoreForAllianceNumbers(match.blueAllianceTeamNumbers)
    match.calculatedData.sdPredictedRedScore = calc.stdDevPredictedScoreForAllianceNumbers(match.redAllianceTeamNumbers)
    match.calculatedData.predictedBlueAutoQuest = calc.getAutoQuestChanceForAllianceWithNumbers(match.redAllianceTeamNumbers)
    match.calculatedData.predictedRedAutoQuest = calc.getAutoQuestChanceForAllianceWithNumbers(match.blueAllianceTeamNumbers)
    match.calculatedData.blueWinChance = calc.winChanceForMatchForAllianceIsRed(match, False)
    match.calculatedData.redWinChance = calc.winChanceForMatchForAllianceIsRed(match, True)
    match.calculatedData.predictedBlueRPs = calc.predictedRPsForAllianceForMatch(False, match)
    match.calculatedData.predictedRedRPs = calc.predictedRPsForAllianceForMatch(True, match)
    '''
