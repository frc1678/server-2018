#Last Updated: 2/7/18
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

    #TIMD CALCS - We're just getting started

    def checkAutoForConflict(self):
        # Need to know our AUTOs first
        return False

    def getDrivingAbility(self, timd):
        # Wait for calculations
        return timd.rankAgility

    def getClimbAttempts(self, climbData):
        return len([climbType[climbAttempt]['didSucceed'] for climbType in climbData for climbAttempt in climbType if climbType[climbAttempt]['didSucceed'] != None])
            
    def getClimbTime(self, climbData):
        times = sorted([climbType[climbAttempt][climbAttemptTag] for climbType in climbData for climbAttempt in climbType for climbAttemptTag in climbType[climbAttempt] if climbType[climbAttempt]['didSucceed'] != None and (climbAttemptTag == 'startTime' or climbAttemptTag == 'endTime')])
        return (times[-1] - times[0])

    def getTotalAttemptsForValueListDicts(self, success, listDicts):
        return len([attempt['didSucceed'] for attempt in listDicts if attempt['didSucceed'] == success])

    def getTotalSuccessForListListDicts(self, listListDicts):
        return sum([len([attempt['didSucceed'] for attempt in listDicts if attempt['didSucceed'] == True]) for listDicts in listListDicts])

    def getAvgSuccessTimeForListDicts(self, listDicts):
        valuesList = [(attempt['endTime']-attempt['startTime']) for attempt in listDicts if attempt['didSucceed'] == True]
        return sum(valuesList)/float(len(valuesList))

    def getCanGroundIntake(self, team):
        return True if (team.calculatedData.avgNumGroundIntake) > 0 else False

    #OVERALL DATA

    #Standard Deviation: Variation of a set of data values, or lowercase sigma
    #Lowercase sigma = sqrt((Sum * (|x - mean|^2)) / n)       (^2 = squared or **2 in python)
    #Z Score: Number of standard deviations something is from the mean
    #http://stattrek.com/statistics/dictionary.aspx?definition=z%20score
    #Z Score = (X - Population Parameter of the mean) / Lowercase sigma
        #R Score: Method of testing college students academically in Quebec which we use for team and robot abilities
        #http://www.goforaplus.com/en/understanding-r-score/
        #R Score = (Z Score + ISG + C) * D       (ISG = Indicator of Group Strength, C & D are constants)

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

    #TBA INVOLVEMENT FOR SCORE BREAKDOWN - Add real keys for score_breakdown once they come out

    '''
    def getPointsEarnedOnScaleForAllianceAuto(self, match, allianceIsRed):
        return self.TBAC.getScoreBreakdownForMatch(match.number)['redScalePointsAuto'] if allianceIsRed else self.TBAC.getScoreBreakdownForMatch(match.number)['blueScalePointsAuto']

    def getPointsEarnedOnScaleForAllianceTele(self, match, allianceIsRed):
        return self.TBAC.getScoreBreakdownForMatch(match.number)['redScalePointsTele'] if allianceIsRed else self.TBAC.getScoreBreakdownForMatch(match.number)['blueScalePointsTele']

    def getPointsEarnedOnAllianceSwitchForAllianceAuto(self, match, allianceIsRed):
        return self.TBAC.getScoreBreakdownForMatch(match.number)['redAllianceSwitchPointsAuto'] if allianceIsRed else self.TBAC.getScoreBreakdownForMatch(match.number)['blueAllianceSwitchPointsAuto']

    def getPointsEarnedOnAllianceSwitchForAllianceTele(self, match, allianceIsRed):
        return self.TBAC.getScoreBreakdownForMatch(match.number)['redAllianceSwitchPointsTele'] if allianceIsRed else self.TBAC.getScoreBreakdownForMatch(match.number)['blueAllianceSwitchPointsTele']
        
    #Save for in case tba api doesn't come out with score_breakdown
    '''

    def getPointsEarnedOnScaleForAllianceAuto(self, match, allianceIsRed):
        print(self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed))
        print([item for sublist in [timd.scaleAttemptAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)] for item in sublist])
        allianceScaleSuccessEndTimes = [round(attempt.endTime + 0.499) for attempt in filter(lambda x: x.didSucceed == True, [item for sublist in [timd.scaleAttemptAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)] for item in sublist])]
        opponentScaleSuccessEndTimes = [round(attempt.endTime + 0.499) for attempt in filter(lambda x: x.didSucceed == True, [item for sublist in [timd.scaleAttemptAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)] for item in sublist])]
        print(allianceScaleSuccessEndTimes)
        print(opponentScaleSuccessEndTimes)
        dictEndTimes = sorted(({time : True for time in allianceScaleSuccessEndTimes}.update({time : False for time in opponentScaleSuccessEndTimes})).update({15 : 0}))
        allianceScore, opponentScore, allianceCubeScore, opponentCubeScore = 0, 0, 0, 0
        oldTime = dictEndTimes.keys()[0]
        for time, alliance in dictEndTimes:
            if allianceCubeScore > opponentCubeScore:
                allianceScore += (time - oldTime) * 2
            elif allianceCubeScore < opponentCubeScore:
                opponentScore += (time - oldTime) * 2
            if alliance:
                allianceCubeScore ++ 1
            else:
                opponentCubeScore ++ 1
        return [allianceScore, opponentScore, allianceCubeScore, opponetCubeScore]

    def getPointsEarnedOnScaleForAllianceTele(self, match, allianceIsRed, allianceCubeScore, opponentCubeScore):
        allianceScaleSuccessEndTimes = [round(attempt.endTime + 0.499) for attempt in filter(lambda x: x.didSucceed == True, [item for sublist in [timd.scaleAttemptTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)] for item in sublist])]
        opponentScaleSuccessEndTimes = [round(attempt.endTime + 0.499) for attempt in filter(lambda x: x.didSucceed == True, [item for sublist in [timd.scaleAttemptTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)] for item in sublist])]
        dictEndTimes = sorted({time : True for time in allianceScaleSuccessEndTimes} + {time : False for time in opponentScaleSuccessEndTimes} +  + {135 : 0})
        allianceScore, opponentScore = 0, 0
        oldTime = dictEndTimes.keys()[0]
        for time, alliance in dictEndTimes:
            if allianceCubeScore > opponentCubeScore:
                allianceScore += (time - oldTime)
            elif allianceCubeScore < opponentCubeScore:
                opponentScore += (time - oldTime)
            if alliance:
                allianceCubeScore ++ 1
            else:
                opponentCubeScore ++ 1
        positionEndOfAuto = 'alliance' if allianceCubeScore > opponentCubeScore else 'neutral' if allianceCubeScore == opponentCubeScore else 'opponent'
        return [allianceScore, opponentScore, positionEndOfAuto]

    #PREDICTIONS - The real juicy stuff

    def predictedParkForTeam(self, team):
        return (team.calculatedData.totalNumParks / (team.numMatchesPlayed - team.calculatedData.numSuccessfulClimbs))

    def predictedParkForAlliance(self, match, allianceIsRed):
        return reduce(lambda x, y: x + y, [self.su.getTeamForNumber(teamNumber).calculatedData.predictedPark for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])])

    def levitateProbabilityForAlliance(self, match, allianceIsRed):
        return 1 - reduce(lambda x, y: x * y, [1 - self.su.getTeamForNumber(teamNumber).calculatedData.didThreeExchangeInputPercentage for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])])

    def predictedAutoRunForAlliance(self, match, allianceIsRed):
        return reduce(lambda x, y: x * y, [self.su.getTeamForNumber(teamNumber).calculatedData.autoRunPercentage for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])])

    def predictedFaceTheBossForTeamInMatch(self, match, team):
        climbPercentages = {'sc' : team.calculatedData.soloClimbPercentage, 'aa' : team.calculatedData.activeAssistClimbPercentage, 'al' : team.calculatedData.activeLiftClimbPercentage, 'ancl' : team.calculatedData.activeNoClimbLiftClimbPercentage, 'ac' : team.calculatedData.assistedClimbPercentage}
        return (max(climbPercentages, key = (lambda k: climbPercentages[k])), climbPercentages[max(climbPercentages, key = (lambda key: climbPercentages[key]))]) 

    def predictedFaceTheBoss(self, match, allianceIsRed):
        climbPercentages = dict([self.predictedFaceTheBossForTeamInMatch(match, team) for team in self.su.getAllianceForMatch(match, allianceIsRed)])
        a = {x : climbPercentages[x] for x in climbPercentages if x == 'sc' or x == 'ac'}
        b = {x : climbPercentages[x] for x in climbPercentages if x == 'aa' or x == 'al' or x == 'ancl'}
        try: 
            a = sorted(a.values())[-1] * sorted(a.values())[-2]
            return max((max(b.values()), a))
        except:
            pass
        return max(b.values())

    def predictedScaleAuto(self, match, allianceIsRed):
        return max([self.su.getTeamForNumber(teamNumber).calculatedData.scaleSuccessPercentageAuto for teamNumber in [match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers]])
    
    def predictedSwitchAuto(self, match, allianceIsRed):
        return max([self.su.getTeamForNumber(teamNumber).calculatedData.allianceSwitchSuccessPercentageAuto for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])])

    def predictedScaleTimeAuto(self, match, allianceIsRed):
        return (sorted([self.su.getTeamForNumber(teamNumber) for teamNumber in [match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers]], key = lambda tm: tm.calculatedData.scaleSuccessPercentageAuto)[0]).calculatedData.avgScaleTimeAuto

    def predictedSwitchTimeAuto(self, match, allianceIsRed):
        return (sorted([self.su.getTeamForNumber(teamNumber) for teamNumber in [match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers]], key = lambda tm: tm.calculatedData.allianceSwitchSuccessPercentageAuto)[0]).calculatedData.avgAllianceSwitchTimeAuto

    def predictedRPsForAlliance(self, match, allianceIsRed):
        return self.predictedWinRP(match, allianceIsRed) + self.predictedAutoQuestRP(match, allianceIsRed) + self.predictedFaceTheBossRP(match, allianceIsRed)

    def predictedWinRP(self, match, allianceIsRed):
        if allianceIsRed:
            return 2 if match.predictedRedScore > match.predictedBlueScore else 1 if match.predictedRedScore == match.predictedBlueScore else 0
        return 2 if match.predictedBlueScore > match.predictedRedScore else 1 if match.predictedBlueScore == match.predictedRedScore else 0

    def predictedAutoQuestRP(self, match, allianceIsRed):
        return self.predictedAutoRunForAlliance(match, allianceIsRed) * self.predictedSwitchAuto(match, allianceIsRed)

    def predictedFaceTheBossRP(self, match, allianceIsRed):
        return self.predictedFaceTheBoss(match, allianceIsRed) * match.redLevitateProbability if allianceIsRed else self.predictedFaceTheBoss(match, allianceIsRed) * match.blueLevitateProbability

    def predictedScalePointsAuto(self, match, allianceIsRed):
        return (15 - self.predictedScaleTimeAuto(match, allianceIsRed)) * 2 * self.predictedScaleAuto(match, allianceIsRed)

    def predictedSwitchPointsAuto(self, match, allianceIsRed):
        return (15 - self.predictedSwitchTimeAuto(match, allianceIsRed)) * 2 * self.predictedSwitchAuto(match, allianceIsRed)

    def predictedScoreForAllianceAuto(self, match, allianceIsRed):
        return 5 * self.predictedAutoRunForAlliance(match, allianceIsRed) + 2 * self.predictedSwitchAuto(match, allianceIsRed) + 2 * self.predictedScaleAuto(match, allianceIsRed) + [self.predictedScalePointsAuto(match, allianceIsRed) / (self.predictedScalePointsAuto(match, allianceIsRed) + self.predictedScalePointsAuto(match, not allianceIsRed))] * min(30, self.predictedScalePointsAuto(match, allianceIsRed) + self.predictedScalePointsAuto(match, not allianceIsRed)) + self.predictedSwitchPointsAuto(match, allianceIsRed)

    def predictedScoreForAlliance(self, match, allianceIsRed):
        return self.predictedScoreForAllianceAuto(match, allianceIsRed) + self.predictedScoreForAllianceTele(match, allianceIsRed) + (self.predictedFaceTheBoss(match, allianceIsRed) * 60)

    #ABILITIES AND POINT CALCULATIONS - please help

    def getPointsPerVaultCube(self):
        return avg([self.getPointsPerVaultCubeForMatch(match) for match in self.su.getCompletedMatchesInCompetition()])

    def getPointsPerVaultCubeForMatch(self, match):
        levitate = 60 if match.redCubesForPowerUp['Levitate'] == 3 and match.blueCubesForPowerUp['Levitate'] == 3 else 30 if match.redCubesForPowerUp['Levitate'] == 3 or match.blueCubesForPowerUp['Levitate'] == 3 else 0
        return (((sum(match.redCubesInVaultFinal.values()) + sum(match.redCubesInVaultFinal.values())) * 5) + levitate) / (sum(match.redCubesInVaultFinal.values()) + sum(match.redCubesInVaultFinal.values()))

    def getPointsPerScaleCube(self):
        return sum([self.getPointsPerScaleCubeForMatch(match) for match in self.comp.matches]) / len(self.su.getCompletedMatchesInCompetition())

    def getPointsPerScaleCubeForMatch(self, match):
        return avg((self.getPointsPerScaleCubeForAlliance(match, True), self.getPointsPerScaleCubeForAlliance(match, False)))

    def getPointsPerScaleCubeForAlliance(self, match, allianceIsRed):
        return self.getPointsEarnedOnScaleForAlliance(match, allianceIsRed) / sum([timd.calculatedData.numScaleSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)])

    def getPointsPerAllianceSwitchCube(self):
        return sum([self.getPointsPerAllianceSwitchCubeForMatch(match) for match in self.comp.matches]) / len(self.su.getCompletedMatchesInCompetition())
    
    def getPointsPerAllianceSwitchCubeForMatch(self, match):
        return avg((self.getPointsPerAllianceSwitchCubeForAlliance(match, True), self.getPointsPerAllianceSwitchCubeForAlliance(match, False)))

    def getPointsPerAllianceSwitchCubeForAlliance(self, match, allianceIsRed):
        return avg((self.getPointsPerOpponentSwitchCube(match, not allianceIsRed) / (sum([timd.calculatedData.numOpponentSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)]) + sum([timd.calculatedData.numOpponentSwitchSuccessAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)]) + sum([timd.calculatedData.numAllianceSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)]) + sum([timd.calculatedData.numAllianceSwitchSuccessAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)])), self.getPointsEarnedOnAllianceSwitchForAllianceTele(match, allianceIsRed) / (sum([timd.calculatedData.numOpponentSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)]) + sum([timd.calculatedData.numOpponentSwitchSuccessAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)]) + sum([timd.calculatedData.numAllianceSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)]) + sum([timd.calculatedData.numAllianceSwitchSuccessAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)]))))

    def getPointsPerOpponentSwitchCube(self):
        return sum([self.getPointsPerOpponentSwitchCubeForMatch(match) for match in self.comp.matches]) / len(self.su.getCompletedMatchesInCompetition())

    def getPointsPerOpponentSwitchCubeForMatch(self, match):
        return avg((self.getPointsPerOpponentSwitchCubeForAlliance(match, True), self.getPointsPerOpponentSwitchCubeForAlliance(match, False)))

    def getPointsPerOpponentSwitchCubeForAlliance(self, match, allianceIsRed):
        return (155 - (self.getPointsEarnedOnAllianceSwitchForAllianceTele(match, not allianceIsRed) + self.getPointsEarnedOnAllianceSwitchForAllianceAuto(match, not allianceIsRed))) / (sum([timd.calculatedData.numOpponentSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)]) + sum([timd.calculatedData.numOpponentSwitchSuccessAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)]) + sum([timd.calculatedData.numAllianceSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)]) + sum([timd.calculatedData.numAllianceSwitchSuccessAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)]))

    def getTeleopExchangeAbilityForAlliance(self, match, allianceIsRed):
        return min(9, sum([self.su.getTeamForNumber(teamNumber).calculatedData.avgNumExchangeInput for teamNumber in [match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers]])) * 5 + (match.redLevitateProbabilility if allianceIsRed else match.blueLevitateProbability) * 30

    def getTeleopScaleAbilityForTeam(self, team):
        return (team.calculatedData.avgCubesPlacedInScaleTele) * self.getPointsPerScaleCube() 

    def getTeleopScaleAbilityForAlliance(self, match, allianceIsRed):
        return sum([self.getTeleopScaleAbilityForTeam(team) for team in self.su.getAllianceForMatch(match, allianceIsRed)])

    def getTeleopAllianceSwitchAbilityForTeam(self, team):
        return (team.calculatedData.avgAllianceSwitchCubesTele) * self.getPointsPerAllianceSwitchCube() 

    def getTeleopScaleAbilityForAlliance(self, match, allianceIsRed):
        return sum([self.getTeleopAllianceSwitchAbilityForTeam(team) for team in self.su.getAllianceForMatch(match, allianceIsRed)])

    def getDrivingAbilityForTeam(self, team):
        return team.calculatedData.avgAgility

    def getFirstPickAbilityForTeam(self, team):
        #Fix this
        autoPoints = 1
        scalePoints = 1
        switchPoints = 1
        groundPickup = 1 if team.calculatedData.canGroundIntake else 0
        exchangePoints = team.calculatedData.teleopExchangeAbility * self.getPointsPerVaultCube()
        drivingAbility = team.calculatedData.avgDrivingAbility
        return (drivingAbility + exchangePoints + switchPoints + autoPoints) + ((switchPoints + scalePoints) * groundPickup)
    
    # def recentDrivingAbility(self, team):

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
    def cumulativeParkAndClimbPointsForTeam(self, team):
        parkPoints = (team.calculatedData.totalNumParks or 0) * 5
        climbPoints = round(team.calculatedData.climbPercentage * float(team.numMatchesPlayed)) * 30
        return parkPoints + climbPoints

    def cumulativeMatchPointsForTeam(self, team):
        allMatches = self.su.getCompletedMatchesForTeam(team)
        scoreFunc = lambda m: self.su.getFieldsForAllianceForMatch(team in match.redAllianceTeamNumbers, match)[0]
        return sum([scoreFunc(match) for match in allMatches])

    def cumulativePredictedMatchPointsForTeam(self, team):
        matches = filter(lambda m: not self.su.matchIsCompleted(m), self.su.getMatchesForTeam(team))
        return sum([self.predictedScoreForAlliance(self.su.getAllianceForTeamInMatch(team, match)) for match in matches]) + self.cumulativeMatchPointsForTeam(team)

    def getSeedingFunctions(self): #Functions to rank teams by for actual seedings, taken as a parameter in the 'teamsSortedByRetrievalFunctions' function
        return [lambda t: t.calculatedData.actualNumRPs, lambda t: self.cumulativeParkAndClimbPointsForTeam(t)]

    def getPredictedSeedingFunctions(self):  #Functions to rank teams by for predicted seedings, taken as a parameter in the 'teamsSortedByRetrievalFunctions' function
        return [lambda t: self.predictedNumberOfRPs(t), lambda t: self.cumulativePredictedMatchPointsForTeam(t)]

    def predictedNumberOfRPs(self, team): #Get average predicted RPs based on predicted score RPs and other parameters
        predictedRPsFunction = lambda m: self.predictedRPsForAllianceForMatch(self.su.getTeamAllianceIsRedInMatch(team, m), m)
        predicted = [predictedRPsFunction(m) for m in self.su.getMatchesForTeam(team) if not self.su.matchIsCompleted(m) and predictedRPsFunction(m) != None]
        return np.mean([np.mean(predicted), self.actualNumberOfRPs(team)]) if len(predicted) else self.actualNumberOfRPs(team)

    def actualNumberOfRPs(self, team):
        return self.getAverageForDataFunctionForTeam(team, lambda tm: tm.calculatedData.numRPs)

    def scoreRPsGainedFromMatchWithScores(self, score, opposingScore):
        return 1 if score == opposingScore else 2 * (score > opposingScore)

    def RPsGainedFromMatchForAlliance(self, allianceIsRed, match):
        winRPs = self.scoreRPsGainedFromMatchWithScores(match.redScore, match.blueScore) if allianceIsRed else self.scoreRPsGainedFromMatchWithScores(match.blueScore, match.redScore)
        if allianceIsRed:
            autoQuestRP = 1 if match.redDidAutoQuest else 0
            faceTheBossRP = 1 if match.redDidFaceBoss else 0
        else:
            autoQuestRP = 1 if match.blueDidAutoQuest else 0
            faceTheBossRP = 1 if match.redDidFaceBoss else 0
        return winRPs + autoQuestRP + faceTheBossRP

    def predictedRPsForAllianceForMatch(self, allianceIsRed, match):
        alliance = map(self.su.replaceWithAverageIfNecessary, self.su.getAllianceForMatch(match, allianceIsRed)) #Gets the correct alliance, either red or blue based on the boolean
        scoreRPs = 2 * (self.getWinChanceForMatchForAllianceIsRed(match, allianceIsRed) or 0)
        boilerRPs = self.get40KilopascalChanceForAlliance(alliance)
        rotorRPs = self.getAllRotorsTurningChanceForAlliance(alliance)
        RPs = scoreRPs + boilerRPs + rotorRPs
        return RPs if not math.isnan(RPs) else None

    def teamsSortedByRetrievalFunctions(self, retrievalFunctions):
        return sorted(self.cachedComp.teamsWithMatchesCompleted, key = lambda t: (retrievalFunctions[0](t) or 0, retrievalFunctions[1](t) or 0), reverse = True)

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
                     (lambda t: t.calculatedData.avgDefense, self.cachedComp.defenseZScores),
                     (lambda t: t.calculatedData.avgDrivingAbility, self.cachedComp.drivingAbilityZScores)]

    def cacheSecondTeamData(self):
        print('> Caching Second Team Data...')
        [self.rValuesForAverageFunctionForDict(func, dictionary) for (func, dictionary) in self.rScoreParams()]
        map(self.doSecondCachingForTeam, self.comp.teams)
        try:
            self.cachedComp.actualSeedings = self.TBAC.makeEventRankingsRequest()
        except Exception as e:
            self.cachedComp.actualSeedings = self.teamsSortedByRetrievalFunctions(self.getSeedingFunctions())
        # self.cachedComp.predictedSeedings = self.teamsSortedByRetrievalFunctions(self.getPredictedSeedingFunctions())
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
        self.comp.updateTIMDsFromFirebase()
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
            print(calculatedTIMDs)
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
            print('Saru')
            self.doMatchesCalculations()
            print('Koko')
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