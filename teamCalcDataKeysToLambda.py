#Last Updated: 8/26/17
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
        
        avgBadDecisions = lambda tm: tm.numBadDecisions, 
        avgCubesFumbledAuto = lambda tm: tm.numCubesFumbledAuto,
        avgCubesFumbledTele = lambda tm: tm.numCubesFumbledTele,
        avgExchangeInput = lambda tm: tm.numExchangeInput,
        avgGoodDecisions = lambda tm: tm.numGoodDecisions,
        avgGroundIntakeTele = lambda tm: tm.numGroundIntakeTele,
        avgGroundPortalIntakeTele = lambda tm: tm.numGroundPortalIntakeTele,
        avgHumanPortalIntakeTele = lambda tm: tm.numHumanPortalIntakeTele,
        avgGroundPyramidIntakeAuto = lambda tm: tm.numGroundPyramidIntakeAuto,
        avgGroundPyramidIntakeTele = lambda tm: tm.numGroundPyramidIntakeTele,
        avgElevatedPyramidIntakeAuto = lambda tm: tm.numElevatedPyramidIntakeAuto,
        avgElevatedPyramidIntakeTele = lambda tm: tm.numElevatedPyramidIntakeTele,
        avgReturnIntake = lambda tm: tm.numReturnIntake,
        avgSpilledCubesAuto = lambda tm: tm.numSpilledCubesAuto,
        avgSpilledCubesTele = lambda tm: tm.numSpilledCubesTele,

        avgAgility = lambda tm: tm.rankAgility,
        avgDefense = lambda tm: tm.rankDefense, 
        avgSpeed = lambda tm: tm.rankSpeed,

        avgRPs = lambda tm: tm.calculatedData.numRPs,
        avgAllianceSwitchSuccessAuto = lambda tm: tm.calculatedData.numAllianceSwitchSuccessAuto,
        avgAllianceSwitchSuccessTele = lambda tm: tm.calculatedData.numAllianceSwitchSuccessTele,
        avgAllianceSwitchFailedAuto = lambda tm: tm.calculatedData.numAllianceSwitchFailedAuto,
        avgAllianceSwitchFailedTele = lambda tm: tm.calculatedData.numAllianceSwitchFailedTele,
        avgOpponentSwitchSuccessAuto = lambda tm: tm.calculatedData.numOpponentSwitchSuccessAuto,
        avgOpponentSwitchSuccessTele = lambda tm: tm.calculatedData.numOpponentSwitchSuccessTele,
        avgOpponentSwitchFailedAuto = lambda tm: tm.calculatedData.numOpponentSwitchFailedAuto,
        avgOpponentSwitchFailedTele = lambda tm: tm.calculatedData.numOpponentSwitchFailedTele,
        avgScaleSuccessAuto = lambda tm: tm.calculatedData.numScaleSuccessAuto,
        avgScaleFailedAuto = lambda tm: tm.calculatedData.numScaleFailedAuto,
        avgScaleSuccessTele = lambda tm: tm.calculatedData.numScaleSuccessTele,
        avgScaleFailedTele = lambda tm: tm.calculatedData.numScaleFailedTele,
        avgCubesPlacedAuto = lambda tm: tm.calculatedData.numCubesPlacedAuto,
        avgCubesPlacedTele = lambda tm: tm.calculatedData.numCubesPlacedTele,
        avgClimbAttempts = lambda tm: tm.calculatedData.numClimbAttempts,

        disabledPercentage = lambda tm: tm.didGetDisabled,
        incapacitatedPercentage = lambda tm: tm.didGetIncapacitated,
        disfunctionalPercentage = lambda tm: tm.calculatedData.isDisfunctional,

        autoRunPercentage = lambda tm: tm.calculatedData.didMakeAutoRun,
        parkPercentage = lambda tm: tm.calculatedData.didPark,

        conflictWithAutoPercentage = lambda tm: tm.calculatedData.didConflictWithAuto,
        )
    mapFuncForCalcAvgsForTeam(team, lambda f: calc.getStandardDeviationForDataFunctionForTeam(team, f), 
        sdLiftoffAbility = lambda tm: tm.calculatedData.liftoffAbility,
        sdHighShotsAuto = lambda tm: tm.calculatedData.numHighShotsAuto,
        sdHighShotsTele = lambda tm: tm.calculatedData.numHighShotsTele,
        sdLowShotsAuto = lambda tm: tm.calculatedData.numLowShotsAuto,
        sdLowShotsTele = lambda tm: tm.calculatedData.numLowShotsTele,
        sdGearsPlacedAuto = lambda tm: tm.calculatedData.numGearsPlacedAuto,
        sdGearsPlacedTele = lambda tm: tm.calculatedData.numGearsPlacedTele,
        )
    mapFuncForCalcAvgsForTeam(team, lambda f: calc.getRecentAverageForDataFunctionForTeam(team, f),
        lfmDisabledPercentage = lambda tm : tm.didStartDisabled,
        lfmIncapacitatedPercentage = lambda tm : tm.didBecomeIncapacitated,
        lfmAvgHighShotsAuto = lambda tm : tm.calculatedData.numHighShotsAuto,
        lfmAvgLowShotsAuto = lambda tm : tm.calculatedData.numLowShotsAuto,
        lmfAvgGearsPlacedAuto = lambda tm: tm.calculatedData.numGearsPlacedAuto, # Should this be lfm?
        lfmAvgGearsPlacedTele = lambda tm : tm.calculatedData.numGearsPlacedTele,
        lfmAvgGearLoaderIntakesTele = lambda tm : tm.numHumanGearIntakesTele,
        lfmAvgHighShotsTele = lambda tm : tm.calculatedData.numHighShotsTele,
        lfmAvgLowShotsTele = lambda tm : tm.calculatedData.numLowShotsTele,
        lfmAvgKeyShotTime = lambda tm : tm.calculatedData.avgKeyShotTime,
        lfmAvgLiftoffTime = lambda tm : tm.liftoffTime,
        lfmLiftoffPercentage = lambda tm : tm.didLiftoff,
        lfmAvgAgility = lambda tm : tm.rankAgility,
        lfmAvgSpeed = lambda tm: tm.rankSpeed,
        lfmAvgBallControl = lambda tm: tm.rankBallControl,
        lfmAvgGearControl = lambda tm: tm.rankGearControl,
        lfmAvgDefense = lambda tm: tm.rankDefense if tm.rankDefense else None #add driverAbility
        )
    cd.autoShootingPositions = calc.getAutoShootingPositions(team)
    calc.getAvgFuncForKeys(team, cd.avgGearsPlacedByLiftAuto, lambda tm: tm.gearsPlacedByLiftAuto)
    calc.getAvgFuncForKeys(team, cd.avgGearsPlacedByLiftTele, lambda tm: tm.gearsPlacedByLiftTele)
    cd.gearScoringPositionsAuto = calc.getGearScoringPositionsAuto(team)

def Rscorecalcs(team, calc):
    cd = team.calculatedData
    cd.RScoreDefense = calc.cachedComp.defenseZScores[team.number]
    cd.RScoreBallControl = calc.cachedComp.ballControlZScores[team.number]
    cd.RScoreGearControl = calc.cachedComp.gearControlZScores[team.number]
    cd.RScoreSpeed = calc.cachedComp.speedZScores[team.number]
    cd.RScoreAgility = calc.cachedComp.agilityZScores[team.number]
    cd.avgDrivingAbility = calc.drivingAbilityForTeam(team)
    # cd.lfmAvgDrivingAbility = calc.recentDrivingAbilityForTeam(team)

def secondCalculationDict(team, calc):
    cd = team.calculatedData
    cd.predictedNumRPs = calc.predictedNumberOfRPs(team)
    cd.firstPickRotorBonusChance = calc.firstPickAllRotorsChance(team)
    try:
        cd.actualNumRPs = calc.getTeamRPsFromTBA(team)
        cd.actualSeed = calc.getTeamSeed(team)
    except Exception as e:
        if team in calc.cachedComp.actualSeedings:
            cd.actualSeed = calc.cachedComp.actualSeedings.index(team) + 1
            cd.actualNumRPs = calc.actualNumberOfRPs(team)
    if team in calc.cachedComp.teamsWithMatchesCompleted:
        cd.RScoreDrivingAbility = calc.cachedComp.drivingAbilityZScores[team.number]
        cd.predictedSeed = calc.cachedComp.predictedSeedings.index(team) + 1
    cd.firstPickAbility = calc.firstPickAbility(team)
    cd.allRotorsAbility = calc.allRotorsAbility(team)

def TIMDCalcDict(timd, calc):
    if (not calc.su.TIMCalculatedDataHasValues(timd.calculatedData)):
        timd.calculatedData = DataModel.CalculatedTeamInMatchData()
    team = calc.su.getTeamForNumber(timd.teamNumber)
    match = calc.su.getMatchForNumber(timd.matchNumber)
    c = timd.calculatedData
    c.numGearsPlacedAuto = calc.getTotalValueForValueDict(timd.gearsPlacedByLiftAuto)
    c.numGearsPlacedTele = calc.getTotalValueForValueDict(timd.gearsPlacedByLiftTele)
    c.avgKeyShotTime = calc.getAvgKeyShotTimeForTIMD(timd, 'Key')
    c.avgHopperShotTime = calc.getAvgKeyShotTimeForTIMD(timd, 'Hopper')
    c.numHighShotsTele = calc.weightFuelShotsForDataPoint(timd, match, 'teleopFuelHigh', timd.highShotTimesForBoilerTele)
    c.numHighShotsAuto = calc.weightFuelShotsForDataPoint(timd, match, 'autoFuelHigh', timd.highShotTimesForBoilerAuto)
    c.numLowShotsTele = calc.weightFuelShotsForDataPoint(timd, match, 'teleopFuelLow', timd.lowShotTimesForBoilerTele)
    c.numLowShotsAuto = calc.weightFuelShotsForDataPoint(timd, match, 'autoFuelLow', timd.lowShotTimesForBoilerAuto)
    c.liftoffAbility = calc.liftoffAbilityForTIMD(timd)
    c.wasDisfunctional = utils.convertFirebaseBoolean(timd.didStartDisabled + utils.convertFirebaseBoolean(timd.didBecomeIncapacitated))
    c.disfunctionalPercentage = utils.convertFirebaseBoolean(timd.didStartDisabled) + 0.5 * utils.convertFirebaseBoolean(timd.didBecomeIncapacitated)
    c.numRPs = calc.RPsGainedFromMatchForAlliance(team.number in match.redAllianceTeamNumbers, match)
    
def averageTeamDict(calc):
    a = calc.averageTeam
    mapFuncForCalcAvgsForTeam(calc.averageTeam, lambda f: calc.getAverageOfDataFunctionAcrossCompetition(f),
        avgBadDecisions = lambda tm: tm.numBadDecisions, 
        avgCubesFumbledAuto = lambda tm: tm.numCubesFumbledAuto,
        avgCubesFumbledTele = lambda tm: tm.numCubesFumbledTele,
        avgExchangeInput = lambda tm: tm.numExchangeInput,
        avgGoodDecisions = lambda tm: tm.numGoodDecisions,
        avgGroundIntakeTele = lambda tm: tm.numGroundIntakeTele,
        avgGroundPortalIntakeTele = lambda tm: tm.numGroundPortalIntakeTele,
        avgHumanPortalIntakeTele = lambda tm: tm.numHumanPortalIntakeTele,
        avgGroundPyramidIntakeAuto = lambda tm: tm.numGroundPyramidIntakeAuto,
        avgGroundPyramidIntakeTele = lambda tm: tm.numGroundPyramidIntakeTele,
        avgElevatedPyramidIntakeAuto = lambda tm: tm.numElevatedPyramidIntakeAuto,
        avgElevatedPyramidIntakeTele = lambda tm: tm.numElevatedPyramidIntakeTele,
        avgReturnIntake = lambda tm: tm.numReturnIntake,
        avgSpilledCubesAuto = lambda tm: tm.numSpilledCubesAuto,
        avgSpilledCubesTele = lambda tm: tm.numSpilledCubesTele,

        avgAgility = lambda tm: tm.rankAgility,
        avgDefense = lambda tm: tm.rankDefense, 
        avgSpeed = lambda tm: tm.rankSpeed,

        avgRPs = lambda tm: tm.calculatedData.numRPs,
        avgAllianceSwitchSuccessAuto = lambda tm: tm.calculatedData.numAllianceSwitchSuccessAuto,
        avgAllianceSwitchSuccessTele = lambda tm: tm.calculatedData.numAllianceSwitchSuccessTele,
        avgAllianceSwitchFailedAuto = lambda tm: tm.calculatedData.numAllianceSwitchFailedAuto,
        avgAllianceSwitchFailedTele = lambda tm: tm.calculatedData.numAllianceSwitchFailedTele,
        avgOpponentSwitchSuccessAuto = lambda tm: tm.calculatedData.numOpponentSwitchSuccessAuto,
        avgOpponentSwitchSuccessTele = lambda tm: tm.calculatedData.numOpponentSwitchSuccessTele,
        avgOpponentSwitchFailedAuto = lambda tm: tm.calculatedData.numOpponentSwitchFailedAuto,
        avgOpponentSwitchFailedTele = lambda tm: tm.calculatedData.numOpponentSwitchFailedTele,
        avgScaleSuccessAuto = lambda tm: tm.calculatedData.numScaleSuccessAuto,
        avgScaleFailedAuto = lambda tm: tm.calculatedData.numScaleFailedAuto,
        avgScaleSuccessTele = lambda tm: tm.calculatedData.numScaleSuccessTele,
        avgScaleFailedTele = lambda tm: tm.calculatedData.numScaleFailedTele,
        avgCubesPlacedAuto = lambda tm: tm.calculatedData.numCubesPlacedAuto,
        avgCubesPlacedTele = lambda tm: tm.calculatedData.numCubesPlacedTele,
        avgClimbAttempts = lambda tm: tm.calculatedData.numClimbAttempts,

        disabledPercentage = lambda tm: tm.didGetDisabled,
        incapacitatedPercentage = lambda tm: tm.didGetIncapacitated,
        disfunctionalPercentage = lambda tm: tm.calculatedData.isDisfunctional,

        autoRunPercentage = lambda tm: tm.calculatedData.didMakeAutoRun,
        parkPercentage = lambda tm: tm.calculatedData.didPark,
        
        conflictWithAutoPercentage = lambda tm: tm.calculatedData.didConflictWithAuto,
        )
    mapFuncForCalcAvgsForTeam(calc.averageTeam, lambda f: calc.getStandardDeviationOfDataFunctionAcrossCompetition(f),
        sdLiftoffAbility = lambda t: t.calculatedData.sdLiftoffAbility,
        sdGearsPlacedTele = lambda t: t.calculatedData.sdGearsPlacedTele,
        sdGearsPlacedAuto = lambda t: t.calculatedData.sdGearsPlacedAuto,
        sdHighShotsAuto = lambda t: t.calculatedData.sdHighShotsAuto,
        sdHighShotsTele = lambda t: t.calculatedData.sdHighShotsTele,
        sdLowShotsAuto = lambda t: t.calculatedData.sdLowShotsAuto,
        sdLowShotsTele = lambda t: t.calculatedData.sdLowShotsTele,
        )

def matchDict(match, calc):
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
