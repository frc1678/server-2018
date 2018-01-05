#Last Updated: 10/12/17
import math
import time
import random
from operator import attrgetter
import numpy as np
import scipy as sp
import scipy.stats as stats
import CacheModel as cache
import DataModel
import utils
import TBACommunicator
import traceback
from teamCalcDataKeysToLambda import *
import multiprocessing
import warnings
from FirstTIMDProcess import FirstTIMDProcess
from schemaUtils import SchemaUtils
from CrashReporter import reportOverestimate
import csv

class Calculator(object):
    '''Does math with scouted data'''
    def __init__(self, competition):
        super(Calculator, self).__init__()
        warnings.simplefilter('error', RuntimeWarning)
        self.comp = competition
        self.TBAC = TBACommunicator.TBACommunicator()
        self.TBAC.eventCode = self.comp.code
        self.ourTeamNum = 1678
        self.monteCarloIterations = 100
        self.su = SchemaUtils(self.comp, self)
        self.cachedTeamDatas = {}
        self.averageTeam = DataModel.Team()
        self.averageTeam.number = -1
        self.reportedTIMDs = []
        self.averageTeam.name = 'Average Team'
        self.writtenMatches = []
        self.teleGearIncrements = [0, 2, 6, 12]
        self.autoGearIncrements = [1, 3, 7, 13]
        self.gearsPerRotor = [1, 2, 4, 6]
        self.gearRangesAuto = [range(1, 3), range(3, 7), range(7, 13), range(13, 14)]
        self.gearRangesTele = [range(2), range(2, 6), range(6, 12), range(12, 13)]
        # self.lifts = ['lift1', 'lift2', 'lift3']
        self.lifts = ['allianceWall', 'hpStation', 'boiler']
        self.shotKeys = {
            'autoFuelLow' : 'avgLowShotsAuto',
            'autoFuelHigh' : 'avgHighShotsAuto',
            'teleopFuelLow' : 'avgLowShotsTele',
            'teleopFuelHigh' : 'avgHighShotsTele'
        }
        self.boilerKeys = {
            'autoFuelLow' : 'lowShotTimesForBoilerAuto',
            'autoFuelHigh' : 'highShotTimesForBoilerAuto',
            'teleopFuelLow' : 'lowShotTimesForBoilerTele',
            'teleopFuelHigh' : 'highShotTimesForBoilerTele'
        }
        self.cachedTeamDatas = {}
        self.cachedComp = cache.CachedCompetitionData()
        self.cachedTeamDatas[self.averageTeam.number] = cache.CachedTeamData(**{'teamNumber': self.averageTeam.number})
        for t in self.comp.teams:
            self.cachedTeamDatas[t.number] = cache.CachedTeamData(**{'teamNumber': t.number})

    def getMissingDataString(self):
        superKeys = ['rankSpeed', 'rankAgility', 'rankDefense', 'rankBallControl', 'rankGearControl']
        excluded = ['liftoffTime', 'superNotes']
        playedTIMDs = self.su.getCompletedTIMDsInCompetition()
        incompleteScoutData = {str(t.teamNumber) + 'Q' + str(t.matchNumber) : [k for k, v in t.__dict__.items() if k != 'calculatedData' and k not in superKeys and k not in excluded and v == None] for t in playedTIMDs}
        incompleteData = {str(t.teamNumber) + 'Q' + str(t.matchNumber) : [k for k, v in t.__dict__.items() if k in superKeys and k not in excluded and v == None] for t in playedTIMDs}
        incompleteData.update(incompleteScoutData)
        missing = {k : v for k, v in incompleteData.items() if v}
        return missing if missing else None

    #Calculated Team Data
    #Hardcore Math
    def getAverageForDataFunctionForTeam(self, team, dataFunction):
        validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.su.getCompletedTIMDsForTeam(team))
        return np.mean(map(dataFunction, validTIMDs)) if validTIMDs else None #returns None if validTIMDs has no elements

    def getRecentAverageForDataFunctionForTeam(self, team, dataFunction):
        timds = self.su.getCompletedTIMDsForTeam(team)
        lfm = filter(lambda t: dataFunction(t) != None, sorted(timds, key = lambda t: t.matchNumber)[len(timds) - 4:])
        return np.mean(map(dataFunction, lfm)) if lfm else None

    def getSumForDataFunctionForTeam(self, team, dataFunction):
        return sum([dataFunction(tm) for tm in self.su.getCompletedTIMDsForTeam(team) if dataFunction(tm) != None])

    def getStandardDeviationForDataFunctionForTeam(self, team, dataFunction):
        validTIMDs = filter(lambda timd: dataFunction(timd) != None, self.su.getCompletedTIMDsForTeam(team))
        return np.std(map(dataFunction, validTIMDs)) if validTIMDs else None

    def getAverageOfDataFunctionAcrossCompetition(self, dataFunction):
        validData = filter(lambda x: x != None, map(dataFunction, self.su.teamsWithCalculatedData()))
        return np.mean(validData) if validData else None

    def getStandardDeviationOfDataFunctionAcrossCompetition(self, dataFunction):
        return utils.rms(map(dataFunction, self.su.teamsWithCalculatedData()))

    def standardDeviationForRetrievalFunctionForAlliance(self, retrievalFunction, alliance):
        return utils.sumStdDevs(map(retrievalFunction, alliance))

    def monteCarloForMeanForStDevForValueFunction(self, mean, stDev, valueFunction):
        if stDev == 0.0:
            return 0.0
        return np.std([valueFunction(np.random.normal(mean, stDev)) for i in range(self.monteCarloIterations)])

    def normalCDF(self, x, mu, sigma):
        #Calculates probability of reaching a threshold (x) based on the mean(mu) and the standard deviation(sigma)
        if sigma == 0.0:
            return int(x <= mu)
        if None not in [x, mu, sigma]:
            #Integrate bell curve from -infinity to x and get complement
            return 1.0 - stats.norm.cdf(x, mu, sigma)

    def welchsTest(self, mean1, mean2, std1, std2, sampleSize1, sampleSize2):
        try:
            t = stats.ttest_ind_from_stats(mean1, std1, sampleSize1, mean2, std2, sampleSize2, False).statistic #False means the variances are unequal
            return t if t != np.nan else mean1 > mean2
        except:
            return 0.0

    def getDF(self, s1, s2, n1, n2):
        #Degrees of freedom to determine shape of Student t-distribution
        if np.nan in [s1, s2, n1, n2] or 0.0 in [n1, n2]:
            return
        try:
            numerator = ((s1 ** 4 / n1) + (s2 ** 4 / n2)) ** 2
            denominator = (s1 ** 8 / ((n1 ** 2) * (n1 - 1))) + (s2 ** 8 / ((n2 ** 2) * (n2 - 1)))
        except:
            numerator = 0.0
            denominator = 0.0
        return numerator / denominator if denominator != 0 else 0.0

    #SHOTS DATA
    def fieldsForShot(self, timd, boilerPoint):
        return sum(map(lambda v: (v.get('numShots') or 0), (timd.__dict__.get(self.boilerKeys[boilerPoint]) or [])))

    def fieldsForShots(self, timd):
        teleHighShots = sum(map(lambda v: (v.get('numShots') or 0), timd.highShotTimesForBoilerTele)) / 3.0
        autoHighShots = sum(map(lambda v: (v.get('numShots') or 0), timd.highShotTimesForBoilerAuto))
        teleLowShots = sum(map(lambda v: (v.get('numShots') or 0), timd.lowShotTimesForBoilerTele)) / 9.0
        autoLowShots = sum(map(lambda v: (v.get('numShots') or 0), timd.lowShotTimesForBoilerAuto)) / 3.0
        return sum([teleHighShots, autoHighShots, teleLowShots, autoLowShots])

    def weightFuelShotsForDataPoint(self, timd, match, boilerPoint, shotKey):
        timds = self.su.getCompletedTIMDsForMatchForAllianceIsRed(match, timd.teamNumber in match.redAllianceTeamNumbers)
        try:
            tbam = filter(lambda m: m['match_number'] == match.number, self.cachedComp.TBAMatches)[0]
            alliance = 'red' if timd.teamNumber in match.redAllianceTeamNumbers else 'blue'
            actualFuel = tbam['scorebreakdown'][alliance][boilerPoint]
            scoutedFuel = sum(map(lambda timd: self.fieldsForShot(timd, boilerPoint), timds))
        except:
            actualFuel = self.getShotPointsForMatchForAlliance(timds, timd.teamNumber in match.redAllianceTeamNumbers, match)
            scoutedFuel = sum(map(lambda t: self.fieldsForShots(t), timds))
        weightage = float(actualFuel) / scoutedFuel if scoutedFuel > 0 else None
        return sum(map(lambda v: (v.get('numShots') or 0), shotKey)) * weightage if weightage != None and weightage > 0 else 0

    def getShotPointsForMatchForAlliance(self, timds, allianceIsRed, match):
        baselinePts = 5 * sum(map(lambda t: True, timds))
        liftoffPts = 50 * sum(map(lambda t: t.didLiftoff, timds))
        fields = self.su.getFieldsForAllianceForMatch(allianceIsRed, match)
        gearPts = fields[2] * 60 + fields[3] * 40
        fuel = fields[0] - fields[4] - gearPts - 15 - liftoffPts if None not in [fields[0], fields[4]] else None
        return fuel

    def getTotalAverageShotPointsForTeam(self, team):
        return sum([(team.calculatedData.avgHighShotsTele or 0) / 3.0, (team.calculatedData.avgLowShotsTele or 0) / 9.0, team.calculatedData.avgHighShotsAuto or 0, (team.calculatedData.avgLowShotsAuto or 0) / 3.0])

    def getTotalAverageRecentShotPointsForTeam(self, team):
        return sum([(team.calculatedData.lfmAvgHighShotsTele or 0) / 3.0, (team.calculatedData.lfmAvgLowShotsTele or 0) / 9.0, team.calculatedData.lfmAvgHighShotsAuto or 0, (team.calculatedData.lfmAvgLowShotsAuto or 0) / 3.0])

    def getStandardDevShotPointsForTeam(self, team):
        return utils.sumStdDevs([(team.calculatedData.sdHighShotsTele or 0) / 3.0, (team.calculatedData.sdLowShotsTele or 0) / 9.0, (team.calculatedData.sdHighShotsAuto or 0), (team.calculatedData.sdLowShotsAuto or 0) / 3.0])

    def getAllBoilerFieldsForKey(self, timd, key):
        shots = timd.highShotTimesForBoilerTele + timd.highShotTimesForBoilerAuto + timd.lowShotTimesForBoilerAuto + timd.lowShotTimesForBoilerTele
        return filter(lambda v: v.get('position') == key, shots)

    def getAvgKeyShotTimeForTIMD(self, timd, key):
        return np.mean(map(lambda t: (t.get('time') or 0), self.getAllBoilerFieldsForKey(timd, key))) if self.getAllBoilerFieldsForKey(timd, key) else None

    def getTotalAverageShotPointsForAlliance(self, alliance):
        return sum(map(self.getTotalAverageShotPointsForTeam, alliance))

    def getStandardDevShotPointsForAlliance(self, alliance):
        return self.standardDeviationForRetrievalFunctionForAlliance(self.getStandardDevShotPointsForTeam, alliance)

    def getAutoShootingPositions(self, team):
        timds = self.su.getCompletedTIMDsForTeam(team)
        return list(set([d.get('position') for timd in timds for d in timd.highShotTimesForBoilerAuto + timd.lowShotTimesForBoilerAuto]))

    #GEARS DATA
    def getTotalValueForValueDict(self, valueDict):
        return sum(filter(lambda v: v, valueDict.values()))

    def getAvgFuncForKeys(self, team, dic, retrievalFunction):
        timds = self.su.getCompletedTIMDsForTeam(team)
        getAvgForKey = lambda t: np.mean(map(lambda tm: (retrievalFunction(tm).get(t) or 0), timds))
        [utils.setDictionaryValue(dic, l, getAvgForKey(l)) for l in self.lifts]

    def getGearScoringPositionsAuto(self, team):
        timds = self.su.getCompletedTIMDsForTeam(team)
        return list(set([lift for lift in self.lifts if team.calculatedData.avgGearsPlacedByLiftAuto.get(lift) != 0]))

    def getAllGearProbabilitiesForTeam(self, team, gearFunc):
        return dict(zip(range(13), map(lambda g: self.probabilityForGearsPlacedForNumberForTeam(team, g, gearFunc), range(13))))

    def getAllGearProbabilitiesForTeams(self, gearFunc):
        dic = {team.number : self.getAllGearProbabilitiesForTeam(team, gearFunc) for team in self.cachedComp.teamsWithMatchesCompleted if team.calculatedData.avgAgility}
        func = lambda k: map(lambda v: (v.get(k) or 0.0), dic.values())
        dic[self.averageTeam.number] = {k : np.mean(func(k)) if func(k) else 0 for k in range(13)}
        return dic

    def getTotalAverageGearsForAlliance(self, alliance):
        gFunc = lambda t: (t.calculatedData.avgGearsPlacedTele or 0) + (t.calculatedData.avgGearsPlacedAuto or 0)
        return sum(map(gFunc, alliance))

    def totalGearsPlacedForTIMD(self, timd):
        return timd.calculatedData.numGearsPlacedAuto + timd.calculatedData.numGearsPlacedTele

    def predictedGearPointsForAlliance(self, alliance):
        autoG = sum(map(lambda t: t.calculatedData.avgGearsPlacedAuto or 0, alliance))
        teleG = sum(map(lambda t: t.calculatedData.avgGearsPlacedTele or 0, alliance))
        autoInd = self.getRotorForIncrementForGears(autoG, self.autoGearIncrements)
        teleInd = self.getRotorForIncrementForGears(teleG + autoG, self.teleGearIncrements[autoInd:])
        return autoInd * 60 + teleInd * 40

    def getRotorForIncrementForGears(self, gears, inc):
        index = filter(lambda g: gears >= g, inc)
        return inc.index(max(index)) + 1 if len(index) else 0

    def getStdDevGearPointsForAlliance(self, alliance):
        totalGearsAuto = sum(map(lambda t: t.calculatedData.avgGearsPlacedAuto or 0, alliance))
        totalGears = self.getTotalAverageGearsForAlliance(alliance)
        sdGearsAuto = self.standardDeviationForRetrievalFunctionForAlliance(lambda t: t.calculatedData.sdGearsPlacedAuto, alliance)
        sdGearsTele = self.standardDeviationForRetrievalFunctionForAlliance(lambda t: t.calculatedData.sdGearsPlacedTele, alliance)
        autoInd = self.getRotorForIncrementForGears(sdGearsAuto, self.autoGearIncrements)
        autoRotors = self.monteCarloForMeanForStDevForValueFunction(totalGearsAuto, sdGearsAuto, lambda g: self.getRotorForIncrementForGears(g, self.autoGearIncrements))
        teleRotors = self.monteCarloForMeanForStDevForValueFunction(totalGears, utils.sumStdDevs([sdGearsAuto, sdGearsTele]), lambda g: self.getRotorForIncrementForGears(g, self.teleGearIncrements[autoInd:]))
        return autoRotors * 60 + teleRotors * 40

    #OVERALL DATA

    #Standard Deviation: Variation of a set of data values, or lowercase sigma
    #Lowercase sigma = sqrt((Sum * (|x - mean|^2)) / n)       (^2 = squared or **2 in python)
    #Z Score: Number of standard deviations something is from the mean
    #http://stattrek.com/statistics/dictionary.aspx?definition=z%20score
    #Z Score = (X - Population Parameter of the mean) / Lowercase sigma
        #R Score: Method of testing college students academically in Quebec which we use for team and robot abilities
        #http://www.goforaplus.com/en/understanding-r-score/
        #R Score = (Z Score + ISG + C) * D       (ISG = Indicator of Group Strength, C & D are constants)

    def liftoffAbilityForTIMD(self, timd):
        team = self.su.getTeamForNumber(timd.teamNumber)
        index = sorted(self.su.getTIMDsForTeam(team), key = lambda t: t.matchNumber).index(timd)
        return 50 * timd.didLiftoff 

    #Gets Z-score for each super data point for all teams
    def rValuesForAverageFunctionForDict(self, averageFunction, d):
        values = map(averageFunction, self.cachedComp.teamsWithMatchesCompleted)
        for index, value in enumerate(values):
            if value == None:
                values[index] = 0
        if not values:
            return
        if not np.std(values):
            zscores = [0.0 for v in values] #Don't calculate z-score if the standard deviation is 0
        else:
            zscores = list(stats.zscore(values))
        [utils.setDictionaryValue(d, self.cachedComp.teamsWithMatchesCompleted[i].number, zscores[i]) for i in range(len(self.cachedComp.teamsWithMatchesCompleted))]

    def drivingAbilityForTeam(self, team):
        gCWeight = 0.22
        bCWeight = 0.0
        spWeight = 0.28
        agWeight = 0.50
        dfWeight = 0.0
        data = [team.calculatedData.RScoreSpeed, team.calculatedData.RScoreGearControl, team.calculatedData.RScoreBallControl, team.calculatedData.RScoreAgility]
        if None in data:
            return
        return team.calculatedData.RScoreSpeed * spWeight + team.calculatedData.RScoreGearControl * gCWeight + team.calculatedData.RScoreAgility * agWeight

    # def recentDrivingAbility(self, team):

    def predictedScoreForAllianceWithNumbers(self, allianceNumbers):
        return self.predictedScoreForAlliance(self.su.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def stdDevPredictedScoreForAlliance(self, alliance):
        alliance = map(self.su.replaceWithAverageIfNecessary, alliance)
        fuelPts = self.getStandardDevShotPointsForAlliance(alliance)
        liftoffPts = utils.sumStdDevs(map(lambda t: (t.calculatedData.sdLiftoffAbility or 0), alliance))
        gearPts = self.getStdDevGearPointsForAlliance(alliance)
        return utils.sumStdDevs([fuelPts, liftoffPts, gearPts])

    def stdDevPredictedScoreForAllianceNumbers(self, allianceNumbers):
        return self.stdDevPredictedScoreForAlliance(self.su.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def predictedScoreForAlliance(self, alliance):
        alliance = map(self.su.replaceWithAverageIfNecessary, alliance)
        fuelPts = self.getTotalAverageShotPointsForAlliance(alliance)
        liftoffPoints = sum(map(lambda t: (t.calculatedData.liftoffAbility or 0), alliance))
        autoGears = sum(map(lambda t: t.calculatedData.avgGearsPlacedAuto or 0, alliance))
        gearPts = self.predictedGearPointsForAlliance(alliance)
        return fuelPts + liftoffPoints + gearPts + 15

    def predictedPlayoffScoreForAlliance(self, alliance):
        return 20 * self.get40KilopascalChanceForAlliance(alliance) + self.predictedScoreForAlliance(alliance) + 100 * self.getAllRotorsTurningChanceForAlliance(alliance)
    
    def firstPickAbility(self, team):
        team = self.su.replaceWithAverageIfNecessary(team)
        ourTeam = self.su.replaceWithAverageIfNecessary(self.su.getTeamForNumber(self.ourTeamNum)) or self.averageTeam
        shots = self.getTotalAverageShotPointsForTeam(team)
        gears = 3 * ((team.calculatedData.avgGearsPlacedAuto or 0) + (team.calculatedData.avgGearsPlacedTele or 0))
        autoBonus = (team.calculatedData.avgGearsPlacedAuto or 0) * 20
        liftoff = team.calculatedData.liftoffAbility or 0
        return gears + shots + liftoff + autoBonus

    def firstPickAllRotorsChance(self, team):
        ourTeam = self.su.getTeamForNumber(self.ourTeamNum) or self.averageTeam
        return self.getAllRotorsTurningChanceForTwoRobotAlliance([ourTeam, team])

    def overallSecondPickAbility(self, team):
        driving = ((team.calculatedData.RScoreDrivingAbility or 0) + 2) * 34
        liftoffAbility = team.calculatedData.liftoffAbility or 0
        gearAbility = 3 * ((team.calculatedData.avgGearsPlacedAuto or 0) + (team.calculatedData.avgGearsPlacedTele or 0))
        autoBonus = (team.calculatedData.avgGearsPlacedAuto or 0) * 20
        functionalPercentage = (1 - team.calculatedData.disfunctionalPercentage)
        return functionalPercentage * (driving + liftoffAbility + gearAbility + autoBonus)

    def predictedScoreForMatchForAlliance(self, match, allianceIsRed):
        return match.calculatedData.predictedRedScore if allianceIsRed else match.calculatedData.predictedBlueScore

    def sdPredictedScoreForMatchForAlliance(self, match, allianceIsRed):
        return match.calculatedData.sdPredictedRedScore if allianceIsRed else match.calculatedData.sdPredictedBlueScore

    def getAvgNumCompletedTIMDsForTeamsOnAlliance(self, alliance):
        return sum(map(lambda t: len(self.su.getCompletedTIMDsForTeam(t)), alliance)) #TODO: WATCHOUT!!!

    def getAvgNumCompletedTIMDsForAlliance(self, alliance):
        return self.getAvgNumCompletedTIMDsForTeamsOnAlliance(alliance)

    def sampleSizeForMatchForAlliance(self, alliance):
        return self.getAvgNumCompletedTIMDsForAlliance(alliance)

    def allRotorsAbility(self, team):
    	driving = ((team.calculatedData.RScoreDrivingAbility or 0) + 2) * 17
        liftoffAbility = 35 * team.calculatedData.liftoffPercentage
        autoBonus = (team.calculatedData.avgGearsPlacedAuto) * 20
        teleBonus = (team.calculatedData.avgGearsPlacedTele + team.calculatedData.avgGearsPlacedAuto) * 40
        functionalPercentage = (1 - team.calculatedData.disfunctionalPercentage)
        return functionalPercentage * (driving + liftoffAbility + autoBonus + teleBonus)

    #PROBABILITIES - Needs to be accurate
    def winChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        alliance = self.su.getAllianceForMatch(match, allianceIsRed)
        predictedScore  = self.predictedScoreForMatchForAlliance(match, allianceIsRed)
        opposingPredictedScore = self.predictedScoreForMatchForAlliance(match, not allianceIsRed)
        sdPredictedScore = self.sdPredictedScoreForMatchForAlliance(match, allianceIsRed)
        sdOpposingPredictedScore = self.sdPredictedScoreForMatchForAlliance(match, not allianceIsRed)
        sampleSize = self.sampleSizeForMatchForAlliance(alliance)
        opposingSampleSize = self.sampleSizeForMatchForAlliance(alliance)
        tscoreRPs = self.welchsTest(predictedScore,
                                       opposingPredictedScore,
                                       sdPredictedScore,
                                       sdOpposingPredictedScore,
                                       sampleSize,
                                       opposingSampleSize)
        df = self.getDF(sdPredictedScore, sdOpposingPredictedScore, sampleSize, opposingSampleSize)
        winChance = stats.t.cdf(tscoreRPs, df)
        return winChance if not math.isnan(winChance) else 0.0

    def getWinChanceForMatchForAllianceIsRed(self, match, allianceIsRed):
        winChance = match.calculatedData.redWinChance if allianceIsRed else match.calculatedData.blueWinChance
        return winChance if not math.isnan((winChance or 0.0)) or not winChance else None

    def get40KilopascalChanceForAlliance(self, alliance):
        alliance = map(self.su.replaceWithAverageIfNecessary, alliance)
        return self.normalCDF(40, self.getTotalAverageShotPointsForAlliance(alliance), self.getStandardDevShotPointsForAlliance(alliance))

    def get40KilopascalChanceForAllianceWithNumbers(self, allianceNumbers):
        self.get40KilopascalChanceForAlliance(self.su.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def totalZProbTeam(self, team, number):
        return self.cachedComp.zGearProbabilities[team.number].get(number) or 0.0

    def getAllRotorsTurningChanceForAlliance(self, alliance):
        alliance = map(self.su.replaceWithAverageIfNecessary, alliance)
        three = (len(alliance) == 3)
        return sum(map(lambda w: sum(map(lambda z: (self.totalZProbTeam(alliance[2], z) if three else 1) * sum(map(lambda y: self.totalZProbTeam(alliance[0], w - y - z) * self.totalZProbTeam(alliance[1], y), range(13))), range(13 if three else 1))), range(12, len(alliance) * 12 + 1)))

    def getAllRotorsTurningChanceForTwoRobotAlliance(self, alliance):
        alliance = map(self.su.replaceWithAverageIfNecessary, alliance)
        return sum(map(lambda w: sum(map(lambda y: self.totalZProbTeam(alliance[0], w - y) * self.totalZProbTeam(alliance[1], y), range(13))), range(12, 25)))

    def probabilityForGearsPlacedForNumberForTeam(self, team, number, gearFunc):
        gearTimds = map(gearFunc, self.su.getCompletedTIMDsForTeam(team))
        return (float(gearTimds.count(number)) / float(len(gearTimds))) or 0

    def getAllRotorsTurningChanceForAllianceWithNumbers(self, allianceNumbers):
        return self.getAllRotorsTurningChanceForAlliance(self.su.teamsForTeamNumbersOnAlliance(allianceNumbers))

    def getAverageRotorPointsPerGear(self):
        matches = self.su.getCompletedMatchesInCompetition()
        rotorPtsFunc = lambda m, a: m['score_breakdown'][a]['autoRotorPoints'] + m['score_breakdown'][a]['teleopRotorPoints'] 
        rotors4Func = lambda m, a: sum(map(lambda n: m['score_breakdown'][a]['rotor' + str(n) + 'Engaged'], range(1, 5))) == 4
        rotorWBonusFunc = lambda m: sum(map(lambda a: rotorPtsFunc(m, a) + (100 if rotors4Func(m, a) else 0), ['red', 'blue']))
        rpts = sum(map(rotorWBonusFunc, self.cachedComp.TBAMatches))
        gFunc = lambda t: (t.calculatedData.numGearsPlacedAuto or 0) + (t.calculatedData.numGearsPlacedTele or 0)
        gpts = sum(map(gFunc, self.su.getCompletedTIMDsInCompetition()))
        return rpts / float(gpts)

    #Seeding
    def autoPointsForAlliance(self, team, match):
        timds = self.su.getTIMDsForMatchForAllianceIsRed(match, team.number in match.redAllianceTeamNumbers)
        fuelPts = sum(map(lambda t: t.calculatedData.numHighShotsAuto + t.calculatedData.numLowShotsAuto / 3.0, timds))
        incsReached = filter(lambda p: sum(map(lambda t: t.calculatedData.numGearsPlacedAuto, timds)) >= p, self.autoGearIncrements)
        gearPts = 60 * (self.autoGearIncrements.index(max(incsReached)) + 1) if incsReached else 0
        return fuelPts + gearPts + 15

    def predictedAutoPointsForAlliance(self, alliance):
        alliance = map(self.su.replaceWithAverageIfNecessary, alliance)
        fuelPts = sum(map(lambda t: (t.calculatedData.avgHighShotsAuto or 0) + (t.calculatedData.avgLowShotsAuto or 0) / 3.0, alliance))
        incsReached = filter(lambda p: sum(map(lambda t: t.calculatedData.avgGearsPlacedAuto or 0, alliance)) >= p, self.autoGearIncrements)
        gearPts = 60 * (self.autoGearIncrements.index(max(incsReached)) + 1) if incsReached else 0
        return fuelPts + gearPts + 15

    def cumulativeAutoPointsForTeam(self, team):
        return sum(map(lambda m: self.autoPointsForAlliance(team, m), self.su.getCompletedMatchesForTeam(team)))

    def cumulativePredictedAutoPointsForTeam(self, team):
        matches = filter(lambda m: not self.su.matchIsCompleted(m), self.su.getMatchesForTeam(team))
        return sum([self.predictedAutoPointsForAlliance(self.su.getAllianceForTeamInMatch(team, match)) for match in matches]) + self.cumulativeAutoPointsForTeam(team)

    def cumulativeMatchPointsForTeam(self, team):
        allMatches = self.su.getCompletedMatchesForTeam(team)
        scoreFunc = lambda m: self.su.getFieldsForAllianceForMatch(team in match.redAllianceTeamNumbers, match)[0]
        return sum([scoreFunc(match) for match in allMatches])

    def cumulativePredictedMatchPointsForTeam(self, team):
        matches = filter(lambda m: not self.su.matchIsCompleted(m), self.su.getMatchesForTeam(team))
        return sum([self.predictedScoreForAlliance(self.su.getAllianceForTeamInMatch(team, match)) for match in matches]) + self.cumulativeMatchPointsForTeam(team)

    def getSeedingFunctions(self): #Functions to rank teams by for actual seedings, taken as a parameter in the 'teamsSortedByRetrievalFunctions' function
        return [lambda t: t.calculatedData.actualNumRPs, lambda t: self.cumulativeMatchPointsForTeam(t), lambda t: self.cumulativeAutoPointsForTeam(t)]

    def getPredictedSeedingFunctions(self):  #Functions to rank teams by for predicted seedings, taken as a parameter in the 'teamsSortedByRetrievalFunctions' function
        return [lambda t: self.predictedNumberOfRPs(t), lambda t: self.cumulativePredictedMatchPointsForTeam(t), lambda t: self.cumulativePredictedAutoPointsForTeam(t)]

    def predictedNumberOfRPs(self, team): #Get average predicted RPs based on predicted score RPs and other parameters
        predictedRPsFunction = lambda m: self.predictedRPsForAllianceForMatch(self.su.getTeamAllianceIsRedInMatch(team, m), m)
        predicted = [predictedRPsFunction(m) for m in self.su.getMatchesForTeam(team) if not self.su.matchIsCompleted(m) and predictedRPsFunction(m) != None]
        return np.mean([np.mean(predicted), self.actualNumberOfRPs(team)]) if len(predicted) else self.actualNumberOfRPs(team)

    def actualNumberOfRPs(self, team):
        return self.getAverageForDataFunctionForTeam(team, lambda tm: tm.calculatedData.numRPs)

    def scoreRPsGainedFromMatchWithScores(self, score, opposingScore):
        return 1 if score == opposingScore else 2 * (score > opposingScore)

    def RPsGainedFromMatchForAlliance(self, allianceIsRed, match):
        ourFields = self.su.getFieldsForAllianceForMatch(allianceIsRed, match)
        opposingFields = self.su.getFieldsForAllianceForMatch(not allianceIsRed, match)
        numRPs = self.scoreRPsGainedFromMatchWithScores(ourFields[0], opposingFields[0])
        gears = (ourFields[2] + ourFields[3]) >= 4 #remove next year
        return numRPs + ourFields[1] + gears

    def predictedRPsForAllianceForMatch(self, allianceIsRed, match):
        alliance = map(self.su.replaceWithAverageIfNecessary, self.su.getAllianceForMatch(match, allianceIsRed)) #Gets the correct alliance, either red or blue based on the boolean
        scoreRPs = 2 * (self.getWinChanceForMatchForAllianceIsRed(match, allianceIsRed) or 0)
        boilerRPs = self.get40KilopascalChanceForAlliance(alliance)
        rotorRPs = self.getAllRotorsTurningChanceForAlliance(alliance)
        RPs = scoreRPs + boilerRPs + rotorRPs
        return RPs if not math.isnan(RPs) else None

    def teamsSortedByRetrievalFunctions(self, retrievalFunctions):
        return sorted(self.cachedComp.teamsWithMatchesCompleted, key = lambda t: (retrievalFunctions[0](t) or 0, retrievalFunctions[1](t) or 0, retrievalFunctions[2](t) or 0), reverse = True)

    def getTeamSeed(self, team):
        return int(filter(lambda x: int(x[1]) == team.number, self.cachedComp.actualSeedings)[0][0])

    def getTeamRPsFromTBA(self, team):
        return filter(lambda x: int(x[1]) == team.number, self.cachedComp.actualSeedings)[0][2]

    #CACHING
    def cacheFirstTeamData(self):
        print('> Caching First Team Data...')
        for team in self.comp.teams:
            self.doCachingForTeam(team)
        self.doCachingForTeam(self.averageTeam)
        self.cachedComp.teamsWithMatchesCompleted = self.su.findTeamsWithMatchesCompleted()

    def rScoreParams(self):
        return [(lambda t: t.calculatedData.avgSpeed, self.cachedComp.speedZScores),
                     (lambda t: t.calculatedData.avgAgility, self.cachedComp.agilityZScores),
                     (lambda t: t.calculatedData.avgBallControl, self.cachedComp.ballControlZScores),
                     (lambda t: t.calculatedData.avgGearControl, self.cachedComp.gearControlZScores),
                     (lambda t: t.calculatedData.avgDefense or 0, self.cachedComp.defenseZScores)]

    def cacheSecondTeamData(self):
        print('> Caching Second Team Data...')
        [self.rValuesForAverageFunctionForDict(func, dictionary) for (func, dictionary) in self.rScoreParams()]
        map(self.doSecondCachingForTeam, self.comp.teams)
        try:
            self.cachedComp.actualSeedings = self.TBAC.makeEventRankingsRequest()
        except Exception as e:
            self.cachedComp.actualSeedings = self.teamsSortedByRetrievalFunctions(self.getSeedingFunctions())
        self.cachedComp.zGearProbabilities = self.getAllGearProbabilitiesForTeams(lambda tm: self.totalGearsPlacedForTIMD(tm))
        self.cachedComp.predictedSeedings = self.teamsSortedByRetrievalFunctions(self.getPredictedSeedingFunctions())
        map(lambda t: Rscorecalcs(t, self), self.cachedComp.teamsWithMatchesCompleted)
        self.rValuesForAverageFunctionForDict(lambda t: t.calculatedData.avgDrivingAbility, self.cachedComp.drivingAbilityZScores)

    def doCachingForTeam(self, team):
        try:
            cachedData = self.cachedTeamDatas[team.number]
        except:
            self.cachedTeamDatas[team.number] = cache.CachedTeamData(**{'teamNumber': team.number})
            cachedData = self.cachedTeamDatas[team.number]
        cachedData.completedTIMDs = self.su.retrieveCompletedTIMDsForTeam(team)

    def doSecondCachingForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]

    def getTBAShotsForTeamForKey(self, team, key):
        TBAMatches = self.cachedComp.TBAMatches
        return sum([match['score_breakdown']['red' if team in self.su.getMatchForNumber(match['match_number']).redAllianceTeamNumbers else 'blue'][key] for match in TBAMatches if self.su.teamInMatch(team, self.su.getMatchForNumber(match['match_number']))])

    def cacheTBAMatches(self):
        try:
            self.cachedComp.TBAMatches = filter(lambda m: m['comp_level'] == 'qm', self.TBAC.makeEventMatchesRequest())
        except:
            print(traceback.format_exc())

    def autoGear(self):
        center = 0
        none = 0
        side = 0
        for team in self.comp.teams:
            if 'lift1' in team.calculatedData.gearScoringPositionsAuto:
                center += 1
            if 'lift2' in team.calculatedData.gearScoringPositionsAuto or 'lift3' in team.calculatedData.gearScoringPositionsAuto:
                side += 1
            if len(team.calculatedData.gearScoringPositionsAuto) == 0:
                none += 1
        print(center / float(center + side + none))
        print(none / float(center + side + none))
        print(side / float(center + side + none))

    #CALCULATIONS
    def getFirstCalculationsForAverageTeam(self):
        averageTeamDict(self)

    def doFirstCalculationsForTeam(self, team):
        if self.su.getCompletedTIMDsForTeam(team):
            if not self.su.teamCalculatedDataHasValues(team.calculatedData):
                team.calculatedData = DataModel.CalculatedTeamData()
            t = team.calculatedData
            firstCalculationDict(team, self)
            print('> Completed first calcs for ' + str(team.number))

    def doSecondCalculationsForTeam(self, team):
        if len(self.su.getCompletedMatchesForTeam(team)):
            secondCalculationDict(team, self)
            print('> Completed second calculations for team ' + str(team.number))

    def doFirstCalculationsForMatch(self, match): #This entire thing being looped is what takes a while
        matchDict(match, self)
        print('> Completed calculations for match ' + str(match.number))

    def doFirstTeamCalculations(self):
        map(self.doFirstCalculationsForTeam, self.comp.teams)
        self.getFirstCalculationsForAverageTeam()

    def doSecondTeamCalculations(self):
        map(self.doSecondCalculationsForTeam, self.comp.teams)
        self.doSecondCalculationsForTeam(self.averageTeam)

    def doThirdTeamCalculations(self):
        map(self.doThirdCalculationsForTeam, self.comp.teams)
        self.doThirdCalculationsForTeam(self.averageTeam)

    def doMatchesCalculations(self):
        map(self.doFirstCalculationsForMatch, self.comp.matches)

    def writeCalculationDiagnostic(self, time):
        with open('./diagnostics.txt', 'a') as file:
            file.write('Time:' + str(time) + '   TIMDs:' + str(len(self.su.getCompletedTIMDsInCompetition())) + '\n')
            file.close()

    def doCalculations(self, PBC):
        isData = len(self.su.getCompletedTIMDsInCompetition()) > 0
        if isData:
            startTime = time.time() #Gets time to later calculate time for a server cycle...
            self.cacheTBAMatches()
            threads = [] #Creates an empty list for timds accessible in multiple processes (manager.list)
            manager = multiprocessing.Manager()
            calculatedTIMDs = manager.list()
            for timd in self.comp.TIMDs:
                #Does TIMD calculations to each TIMD in the competition, and puts the process into a list
                #the calculation results get put into
                thread = FirstTIMDProcess(timd, calculatedTIMDs, self)
                threads.append(thread)
                thread.start()
            #The main function does not continue until all of the TIMD processes are done (join)
            map(lambda t: t.join(), threads)
            #Converts the shared list into a normal list
            self.comp.TIMDs = [timd for timd in calculatedTIMDs]
            self.cacheFirstTeamData()
            self.doFirstTeamCalculations()
            self.cacheSecondTeamData()
            self.doMatchesCalculations()
            self.doSecondTeamCalculations()
            print('> Calculations finished, adding data to firebase')
            PBC.addCalculatedTIMDatasToFirebase(self.su.getCompletedTIMDsInCompetition())
            PBC.addCalculatedTeamDatasToFirebase(self.cachedComp.teamsWithMatchesCompleted)
            PBC.addCalculatedMatchDatasToFirebase(self.comp.matches)
            PBC.addCompInfoToFirebase()
            endTime = time.time()
            # self.autoGear()
            self.writeCalculationDiagnostic(endTime - startTime)
        else:
            print('> No calculations to do...')
