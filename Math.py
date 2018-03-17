#Last Updated: 3/15/18
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
        self.su = SchemaUtils(self.comp, self)
        self.cachedTeamDatas = {}
        self.averageTeam = DataModel.Team()
        self.averageTeam.number = -1
        self.averageTeam.name = 'Average Team'
        self.calcTIMDs = []
        self.pointsPerScaleCube = 20.29 #Backup in case of calc failure
        self.pointsPerAllianceSwitchCube = 52.41
        self.pointsPerOpponentSwitchCube = 22.14
        self.cachedTeamDatas = {}
        self.cachedComp = cache.CachedCompetitionData()
        self.cachedTeamDatas[self.averageTeam.number] = cache.CachedTeamData(**{'teamNumber': self.averageTeam.number})
        for t in self.comp.teams:
            self.cachedTeamDatas[t.number] = cache.CachedTeamData(**{'teamNumber': t.number})

    def getMissingDataString(self):
        superKeys = ['rankSpeed', 'rankAgility', 'rankDefense']
        excluded = ['climb', 'superNotes']
        playedTIMDs = self.su.getCompletedTIMDsInCompetition()
        incompleteScoutData = {str(t.teamNumber) + 'Q' + str(t.matchNumber) : [k for k, v in t.__dict__.items() if k != 'calculatedData' and k not in superKeys and k not in excluded and v == None] for t in playedTIMDs}
        incompleteData = {str(t.teamNumber) + 'Q' + str(t.matchNumber) : [k for k, v in t.__dict__.items() if k in superKeys and k not in excluded and v == None] for t in playedTIMDs}
        incompleteData.update(incompleteScoutData)
        missing = {k : v for k, v in incompleteData.items() if v}
        return missing if missing else None

    #CALCULATED TEAM DATA - Hardcore Math

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
        except KeyboardInterrupt:
            break
        except:
            return 0.0

    def getDF(self, s1, s2, n1, n2):
        #Degrees of freedom to determine shape of Student t-distribution
        if np.nan in [s1, s2, n1, n2] or 0.0 in [n1, n2]:
            return
        try:
            numerator = ((s1 ** 4 / n1) + (s2 ** 4 / n2)) ** 2
            denominator = (s1 ** 8 / ((n1 ** 2) * (n1 - 1))) + (s2 ** 8 / ((n2 ** 2) * (n2 - 1)))
        except KeyboardInterrupt:
            break
        except:
            numerator = 0.0
            denominator = 0.0
        return numerator / denominator if denominator != 0 else 0.0

    #NON-SYSTEMATIC TEAM CALCS - When averages aren't good enough

    def getMaxScaleCubes(self, team):
        return max([(timd.calculatedData.numScaleSuccessTele + timd.calculatedData.numScaleSuccessAuto) for timd in self.su.getCompletedTIMDsForTeam(team)])

    def getPercentageForClimbType(self, team, climbType):
        return utils.avg([climb[1]['didSucceed'] if climb[0] == climbType else False for x in self.su.getCompletedTIMDsForTeam(team) for attempt in x.climb for climb in attempt.items()])

    def getPercentageForActiveClimbType(self, team, didClimb, liftType):
        return utils.avg([climb[1]['didSucceed'] if climb[0] == 'activeLift' and climb[1].get('didClimb', None) == didClimb and climb[1].get('partnerLiftType', None) == liftType else False for x in self.su.getCompletedTIMDsForTeam(team) for attempt in x.climb for climb in attempt.items()])

    def parkPercentageForTeam(self, team):
        parks = float(team.calculatedData.totalNumParks)
        matches = float(team.calculatedData.numMatchesPlayed)
        return (parks / matches)

    def getCanGroundIntake(self, team):
        return True if (team.calculatedData.avgNumGroundIntakeTele + team.calculatedData.avgNumAlliancePlatformIntakeAuto + team.calculatedData.avgNumAlliancePlatformIntakeTele + team.calculatedData.avgNumOpponentPlatformIntakeTele + team.calculatedData.avgNumGroundPyramidIntakeAuto + team.calculatedData.avgNumGroundPyramidIntakeTele + team.calculatedData.avgNumGroundPortalIntakeTele) > 0 else False

    def getCanScoreBothSwitchSidesAuto(self, team):
        return True in [timd.calculatedData.canScoreOppositeSwitchAuto for timd in self.su.getCompletedTIMDsForTeam(team)]

    def getTotalSuperNotes(self, team):
        return [x.superNotes for x in self.su.getCompletedTIMDsForTeam(team)]

    def getAllianceSwitchSuccessPercentageAuto(self, team):
        try:
            return utils.avg(utils.removeNoneFrom([attempt['didSucceed'] for attempt in utils.extendList([timd.allianceSwitchAttemptAuto for timd in self.su.getCompletedTIMDsForTeam(team)])]))
        except:
            return 0.0

    def getAllianceSwitchSuccessPercentageTele(self, team):
        try:
            return utils.avg(utils.removeNoneFrom([attempt['didSucceed'] for attempt in utils.extendList([timd.allianceSwitchAttemptTele for timd in self.su.getCompletedTIMDsForTeam(team)])]))
        except:
            return 0.0

    def getOpponentSwitchSuccessPercentageTele(self, team):
        try:
            return utils.avg(utils.removeNoneFrom([attempt['didSucceed'] for attempt in utils.extendList([timd.opponentSwitchAttemptTele for timd in self.su.getCompletedTIMDsForTeam(team)])]))
        except:
            return 0.0

    def getScaleSuccessPercentageAuto(self, team):
        try:
            return utils.avg(utils.removeNoneFrom([attempt['didSucceed'] for attempt in utils.extendList([timd.scaleAttemptAuto for timd in self.su.getCompletedTIMDsForTeam(team)])]))
        except:
            return 0.0

    def getScaleSuccessPercentageTele(self, team):
        try:
            return utils.avg(utils.removeNoneFrom([attempt['didSucceed'] for attempt in utils.extendList([timd.scaleAttemptTele for timd in self.su.getCompletedTIMDsForTeam(team)])]))
        except:
            return 0.0 

    def getCanPlaceHighLayerCube(self, team):
        return (len(filter(lambda x: x != 1, [attempt['layer'] for attempt in utils.extendList(([timd.scaleAttemptTele for timd in self.su.getCompletedTIMDsForTeam(team)] + [timd.scaleAttemptAuto for timd in self.su.getCompletedTIMDsForTeam(team)])) if attempt['didSucceed'] == True])) > 0)
    
    def getTotalNumHighLayerScaleCubes(self, team):
        return len(filter(lambda x: x != 1, [attempt['layer'] for attempt in utils.extendList(([timd.scaleAttemptTele for timd in self.su.getCompletedTIMDsForTeam(team)] + [timd.scaleAttemptAuto for timd in self.su.getCompletedTIMDsForTeam(team)])) if attempt['didSucceed'] == True]))

    def getPercentSuccessOppositeSwitchSideAuto(self, team):
        try:
            return utils.avg([timd.calculatedData.canScoreOppositeSwitchAuto for timd in self.su.getCompletedTIMDsForTeam(team) if timd.calculatedData.switchIsOpposite])
        except:
            return 0

    #TIMD CALCS - We're just getting started

    def checkAutoForConflict(self):
        return False

    def getCanScoreOppositeSwitch(self, timd, team, match):
        allianceIsRed = self.su.getTeamAllianceIsRedInMatch(team, match)
        try:
            switchIsOpposite = False if ('blue' == match.redSwitch[timd.startingPosition] if allianceIsRed else 'red' != match.blueSwitch[timd.startingPosition]) or timd.startingPosition == 'center' else True
            return True if switchIsOpposite and True in [attempt['didSucceed'] for attempt in timd.allianceSwitchAttemptAuto] else False
        except:
            return False

    def getSwitchIsOpposite(self, timd, team, match):
        allianceIsRed = self.su.getTeamAllianceIsRedInMatch(team, match)
        try:
            return False if ('blue' == match.redSwitch[timd.startingPosition] if allianceIsRed else 'red' != match.blueSwitch[timd.startingPosition]) or timd.startingPosition == 'center' else True
        except:
            return False

    def getDidThreeExchangeInput(self, timd):
        return True if timd.numExchangeInput >= 3 else False

    def getDidClimb(self, climbData):
        return True if True in [climbType[climbAttempt]['didSucceed'] for climbType in climbData for climbAttempt in climbType if climbType[climbAttempt]['didSucceed'] != None] else False

    def getClimbAttempts(self, climbData):
        return len([climbType[climbAttempt]['didSucceed'] for climbType in climbData for climbAttempt in climbType if climbType[climbAttempt]['didSucceed'] != None])
            
    def getClimbTime(self, climbData):
        times = sorted([climbType[climbAttempt][climbAttemptTag] for climbType in climbData for climbAttempt in climbType for climbAttemptTag in climbType[climbAttempt] if climbType[climbAttempt]['didSucceed'] != None and (climbAttemptTag == 'startTime' or climbAttemptTag == 'endTime')])
        if times:
            return (times[-1] - times[0])

    def getTotalAttemptsForValueListDicts(self, success, listDicts):
        return len([attempt['didSucceed'] for attempt in listDicts if attempt['didSucceed'] == success])

    def getTotalSuccessForListListDicts(self, listListDicts):
        return sum([len([attempt['didSucceed'] for attempt in listDicts if attempt['didSucceed'] == True]) for listDicts in listListDicts])

    def getAvgSuccessTimeForListDicts(self, listDicts):
        try:
            valuesList = [(attempt['endTime']-attempt['startTime']) for attempt in listDicts if attempt['didSucceed'] == True]
            return sum(valuesList)/float(len(valuesList))
        except:
            return 0

    def getTotalSuccessForListOfBools(self, boolList):
        try:
            return sum(boolList)
        except:
            return sum(boolList.values())

    def getNumRobotsLifted(self, timd):
        try:
            return [climbType[climbAttempt]['numRobotsLifted'] for climbType in timd.climb for climbAttempt in climbType if climbType[climbAttempt]['didSucceed'] == True][0]
        except:
            return int(timd.calculatedData.didClimb)

    def getTimeToOwnAllianceSwitchAuto(self, timd):
        try:
            sort = sorted([attempt['endTime'] for attempt in timd.allianceSwitchAttemptAuto if attempt['didSucceed'] == True])[0]
            if sort > 15:
                return 15
            else:
                return sort
        except:
            return 15

    def getTimeToOwnScaleAuto(self, timd):
        try:
            sort = sorted([attempt['endTime'] for attempt in timd.scaleAttemptAuto if attempt['didSucceed'] == True])[0]
            if sort > 15:
                return 15
            else:
                return sort
        except:
            return 15

    def getTotalSuccessForListOfBools(self, boolList):
        try:
            return sum(boolList)
        except:
            return sum(boolList.values())

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

    def rValuesForTIMDMatrix(self, rankFunction, d):
        #This function is not currently being used because of the invariation of resulting data
        values = np.full([len(self.cachedComp.teamsWithMatchesCompleted), 10], None, dtype = 'float64')
        for teamNum, team in enumerate(self.cachedComp.teamsWithMatchesCompleted):
            for matchNum, match in enumerate(self.su.getCompletedTIMDsForTeam(team)):
                values[teamNum][matchNum] = rankFunction(match)
        #If the rank hasn't been set, set it to the mean
        mean = np.nanmean(values)
        for teamNum, team in enumerate(values):
            for index, match in enumerate(team):
                if str(match) == str(np.nan):
                    values[teamNum][index] = mean
        if not np.any(values):
            return
        if not np.std(values):
            zscores = [[0.0 for x in values[0]] for v in values]
        else:
            zscores = utils.matrixZscores(values)
        [utils.setDictionaryValue(d, self.cachedComp.teamsWithMatchesCompleted[i].number, zscores[i]) for i in range(len(self.cachedComp.teamsWithMatchesCompleted))]

    #TBA INVOLVEMENT FOR SCORE BREAKDOWN

    def getPointsEarnedOnScaleForAllianceAuto(self, match, allianceIsRed):
        return self.TBAC.getScoreBreakdownForMatch(match.number)['red']['autoScaleOwnershipSec'] if allianceIsRed else self.TBAC.getScoreBreakdownForMatch(match.number)['blue']['autoScaleOwnershipSec']

    def getPointsEarnedOnScaleForAllianceTele(self, match, allianceIsRed):
        return self.TBAC.getScoreBreakdownForMatch(match.number)['red']['teleopScaleOwnershipSec'] if allianceIsRed else self.TBAC.getScoreBreakdownForMatch(match.number)['blue']['teleopScaleOwnershipSec']

    def getPointsEarnedOnAllianceSwitchForAllianceAuto(self, match, allianceIsRed):
        return self.TBAC.getScoreBreakdownForMatch(match.number)['red']['autoSwitchOwnershipSec'] if allianceIsRed else self.TBAC.getScoreBreakdownForMatch(match.number)['blue']['autoSwitchOwnershipSec']

    def getPointsEarnedOnAllianceSwitchForAllianceTele(self, match, allianceIsRed):
        return self.TBAC.getScoreBreakdownForMatch(match.number)['red']['teleopSwitchOwnershipSec'] if allianceIsRed else self.TBAC.getScoreBreakdownForMatch(match.number)['blue']['teleopSwitchOwnershipSec']

    #PREDICTIONS - The real juicy stuff

    def predictedParkForTeam(self, team):
        try:
            return (float(team.calculatedData.totalNumParks) / (sum(self.su.getCompletedTIMDsForTeam(team)) - team.calculatedData.numSuccessfulClimbs))
        except:
            return 0.0

    def predictedParkForAlliance(self, match, allianceIsRed):
        return reduce(lambda x, y: x + y, utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.predictedPark for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])], 0.0))

    def levitateProbabilityForAlliance(self, match, allianceIsRed):
        return 1 - reduce(lambda x, y: x * y, [1 - x for x in utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.didThreeExchangeInputPercentage for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])], 0.0)])

    def predictedAutoRunForAlliance(self, match, allianceIsRed):
        return reduce(lambda x, y: x * y, utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.autoRunPercentage for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])], 1.0))

    def predictedFaceTheBossForTeamInMatch(self, match, team):
        climbPercentages = {'sc' : team.calculatedData.soloClimbPercentage, 'aa' : team.calculatedData.activeAssistClimbPercentage, 'al' : team.calculatedData.activeLiftClimbPercentage, 'ancl' : team.calculatedData.activeNoClimbLiftClimbPercentage, 'ac' : team.calculatedData.assistedClimbPercentage}
        return (max(climbPercentages, key = (lambda k: climbPercentages[k])), climbPercentages[max(climbPercentages, key = (lambda key: climbPercentages[key]))]) 

    def predictedFaceTheBoss(self, match, allianceIsRed):
        climbPercentages = dict([self.predictedFaceTheBossForTeamInMatch(match, team) for team in self.su.getAllianceForMatch(match, allianceIsRed)])
        a = {x : climbPercentages[x] for x in climbPercentages if x == 'sc' or x == 'ac'}
        b = {x : climbPercentages[x] for x in climbPercentages if x == 'aa' or x == 'al' or x == 'ancl'}
        try: 
            a = sorted(a.values())[-1] * sorted(a.values())[-2]
            return max(max(b.values()), a)
        except:
            pass
        try:
            return max(b.values())
        except:
            return 0

    def predictedScaleAuto(self, match, allianceIsRed):
        return max(utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.scaleSuccessPercentageAuto for teamNumber in (match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers)], 0.0))
    
    def predictedSwitchAuto(self, match, allianceIsRed):
        return max(utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.allianceSwitchSuccessPercentageAuto for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])], 0.0))

    def predictedScaleTimeAuto(self, match, allianceIsRed):
        return utils.convertNoneToIdentity((sorted([self.su.getTeamForNumber(teamNumber) for teamNumber in [match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0]], key = lambda tm: tm.calculatedData.scaleSuccessPercentageAuto)[0]).calculatedData.avgScaleTimeAuto, 0.0)

    def predictedSwitchTimeAuto(self, match, allianceIsRed):
        return utils.convertNoneToIdentity((sorted([self.su.getTeamForNumber(teamNumber) for teamNumber in [match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0]], key = lambda tm: tm.calculatedData.allianceSwitchSuccessPercentageAuto)[0]).calculatedData.avgAllianceSwitchTimeAuto, 0.0)

    def predictedTotalNumRPsForTeam(self, team):
        return sum([match.calculatedData.predictedRedRPs if team.number in match.redAllianceTeamNumbers else match.calculatedData.predictedBlueRPs for match in self.su.getCompletedMatchesForTeam(team)])

    def predictedNumRPsForTeam(self, team):
        return utils.avg([match.calculatedData.predictedRedRPs if team.number in match.redAllianceTeamNumbers else match.calculatedData.predictedBlueRPs for match in self.su.getCompletedMatchesForTeam(team)])

    def predictedRPsForAlliance(self, match, allianceIsRed):
        return self.predictedWinRP(match, allianceIsRed) + self.predictedAutoQuestRP(match, allianceIsRed) + self.predictedFaceTheBossRP(match, allianceIsRed)

    def predictedWinRP(self, match, allianceIsRed):
        if allianceIsRed:
            return 2 if match.calculatedData.predictedRedScore > match.calculatedData.predictedBlueScore else 1 if match.calculatedData.predictedRedScore == match.calculatedData.predictedBlueScore else 0
        return 2 if match.calculatedData.predictedBlueScore > match.calculatedData.predictedRedScore else 1 if match.calculatedData.predictedBlueScore == match.calculatedData.predictedRedScore else 0

    def predictedAutoQuestRP(self, match, allianceIsRed):
        return self.predictedAutoRunForAlliance(match, allianceIsRed) * self.predictedSwitchAuto(match, allianceIsRed)

    def predictedFaceTheBossRP(self, match, allianceIsRed):
        return self.predictedFaceTheBoss(match, allianceIsRed) * match.calculatedData.redLevitateProbability if allianceIsRed else self.predictedFaceTheBoss(match, allianceIsRed) * match.calculatedData.blueLevitateProbability

    def predictedScalePointsAuto(self, match, allianceIsRed):
        return (15 - self.predictedScaleTimeAuto(match, allianceIsRed)) * 2 * self.predictedScaleAuto(match, allianceIsRed)

    def predictedSwitchPointsAuto(self, match, allianceIsRed):
        return (15 - self.predictedSwitchTimeAuto(match, allianceIsRed)) * 2 * self.predictedSwitchAuto(match, allianceIsRed)

    #ABILITIES AND POINT CALCULATIONS - Different abilities for teams and alliances

    def getPointsPerVaultCube(self):
        return utils.avg([self.getPointsPerVaultCubeForMatch(match) for match in self.su.getCompletedMatchesInCompetition()])

    def getPointsPerVaultCubeForMatch(self, match):
        levitate = 60 if match.redCubesForPowerup['Levitate'] == 3 and match.blueCubesForPowerup['Levitate'] == 3 else 30 if match.redCubesForPowerup['Levitate'] == 3 or match.blueCubesForPowerup['Levitate'] == 3 else 0
        return (((sum(match.blueCubesInVaultFinal.values()) + sum(match.redCubesInVaultFinal.values())) * 5) + levitate) / utils.convertIdentity(sum(match.redCubesInVaultFinal.values()) + sum(match.redCubesInVaultFinal.values()), 1.0, 0.0)

    def getPointsPerScaleCube(self):
        points = sum([self.getPointsPerScaleCubeForMatch(match) for match in self.comp.matches])
        matches = utils.convertIdentity(len(self.su.getCompletedMatchesInCompetition()),1.0,0.0)
        return points / float(matches)

    def getPointsPerScaleCubeForMatch(self, match):
        return utils.avg([self.getPointsPerScaleCubeForAlliance(match, True), self.getPointsPerScaleCubeForAlliance(match, False)])

    def getPointsPerScaleCubeForAlliance(self, match, allianceIsRed):
        try:
            return (self.getPointsEarnedOnScaleForAllianceAuto(match, allianceIsRed) + self.getPointsEarnedOnScaleForAllianceTele(match, allianceIsRed)) / sum(utils.replaceFromNone([timd.calculatedData.numScaleSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)], 0.0))
        except:
            return 0.0

    def getPointsPerAllianceSwitchCube(self):
        return sum([self.getPointsPerAllianceSwitchCubeForMatch(match) for match in self.comp.matches]) / utils.convertIdentity(len(self.su.getCompletedMatchesInCompetition()), 1.0, 0.0)
    
    def getPointsPerAllianceSwitchCubeForMatch(self, match):
        return utils.avg([self.getPointsPerAllianceSwitchCubeForAlliance(match, True), self.getPointsPerAllianceSwitchCubeForAlliance(match, False)])

    def getPointsPerAllianceSwitchCubeForAlliance(self, match, allianceIsRed):
        try:
            return ((self.getPointsEarnedOnAllianceSwitchForAllianceTele(match, allianceIsRed) + self.getPointsEarnedOnAllianceSwitchForAllianceAuto(match, allianceIsRed)) / (sum(utils.replaceFromNone([timd.calculatedData.numOpponentSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)], 0.0)) + sum(utils.replaceFromNone([timd.calculatedData.numAllianceSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)], 0.0)) + sum(utils.replaceFromNone([timd.calculatedData.numAllianceSwitchSuccessAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)], 0.0))))
        except:
            return 0.0

    def getPointsPerOpponentSwitchCube(self):
        points = sum([self.getPointsPerOpponentSwitchCubeForMatch(match) for match in self.comp.matches])
        matches = len(self.su.getCompletedMatchesInCompetition())
        return points / utils.convertIdentity(float(matches), 1.0, 0.0)

    def getPointsPerOpponentSwitchCubeForMatch(self, match):
        return utils.avg([self.getPointsPerOpponentSwitchCubeForAlliance(match, True), self.getPointsPerOpponentSwitchCubeForAlliance(match, False)])

    def getPointsPerOpponentSwitchCubeForAlliance(self, match, allianceIsRed):
        try:
            return (155 - (self.getPointsEarnedOnAllianceSwitchForAllianceTele(match, not allianceIsRed) + self.getPointsEarnedOnAllianceSwitchForAllianceAuto(match, not allianceIsRed))) / (sum(utils.replaceFromNone([timd.calculatedData.numOpponentSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed)], 0.0)) + sum(utils.replaceFromNone([timd.calculatedData.numAllianceSwitchSuccessTele for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)], 0.0)) + sum(utils.replaceFromNone([timd.calculatedData.numAllianceSwitchSuccessAuto for timd in self.su.getTIMDsForMatchForAllianceIsRed(match, not allianceIsRed)], 0.0)))
        except:
            return 0.0

    def getTeleopExchangeAbilityForTeam(self, team):
        return utils.convertNoneToIdentity(team.calculatedData.avgNumExchangeInputTele, 0.0) * 5 + utils.avg([match.calculatedData.redLevitateProbability if team.number in match.redAllianceTeamNumbers else match.calculatedData.blueLevitateProbability for match in self.su.getCompletedMatchesForTeam(team)]) * 30

    def getTeleopExchangeAbilityForAlliance(self, match, allianceIsRed):
        return min(9, sum(utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.avgNumExchangeInputTele for teamNumber in utils.extendList([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers])], 0.0))) * 5 + (match.calculatedData.redLevitateProbability if allianceIsRed else match.calculatedData.blueLevitateProbability) * 30

    def getTeleopScaleAbilityForTeam(self, team):
        return utils.convertNoneToIdentity(team.calculatedData.avgCubesPlacedInScaleTele, 0.0) * self.pointsPerScaleCube

    def getTeleopScaleAbilityForAlliance(self, match, allianceIsRed):
        return sum(utils.replaceFromNone([self.getTeleopScaleAbilityForTeam(team) for team in self.su.getAllianceForMatch(match, allianceIsRed)], 0.0))

    def getTeleopAllianceSwitchAbilityForTeam(self, team):
        return utils.convertNoneToIdentity(team.calculatedData.avgAllianceSwitchCubesTele, 0.0) * self.pointsPerAllianceSwitchCube

    def getTeleopAllianceSwitchAbilityForAlliance(self, match, allianceIsRed):
        return sum(utils.replaceFromNone([self.getTeleopAllianceSwitchAbilityForTeam(team) for team in self.su.getAllianceForMatch(match, allianceIsRed)], 0.0))

    def getTeleopOpponentSwitchAbilityForTeam(self, team):
        return utils.convertNoneToIdentity(team.calculatedData.avgOpponentSwitchCubesTele, 0.0) * self.pointsPerOpponentSwitchCube

    def getTeleopOpponentSwitchAbilityForAlliance(self, match, allianceIsRed):
        return sum(utils.replaceFromNone([self.getTeleopOpponentSwitchAbilityForTeam(team) for team in self.su.getAllianceForMatch(match, allianceIsRed)], 0.0))

    def getFirstPickAbilityForTeam(self, team):
        autoPoints = ((15 - team.calculatedData.avgTimeToOwnScaleAuto) * 2 + (15 - team.calculatedData.avgTimeToOwnAllianceSwitchAuto) * 2 + team.calculatedData.autoRunPercentage * 5)
        scalePoints = team.calculatedData.teleopScaleAbility
        switchPoints = team.calculatedData.teleopAllianceSwitchAbility + team.calculatedData.teleopOpponentSwitchAbility
        groundPickup = 1 if team.calculatedData.canGroundIntake else 0
        exchangePoints = team.calculatedData.teleopExchangeAbility
        drivingAbility = team.calculatedData.avgDrivingAbility
        climb = (team.calculatedData.avgNumRobotsLifted * 30) * (team.calculatedData.activeLiftClimbPercentage + team.calculatedData.soloClimbPercentage + team.calculatedData.activeAssistClimbPercentage)
        return ((drivingAbility + exchangePoints + autoPoints) + ((switchPoints + scalePoints) * groundPickup))
    
    def getSecondPickAbilityForTeam(self, team):
        autoPoints = ((15 - team.calculatedData.avgTimeToOwnAllianceSwitchAuto) * 2 + team.calculatedData.autoRunPercentage * 5)
        switchPoints = team.calculatedData.teleopAllianceSwitchAbility + team.calculatedData.teleopOpponentSwitchAbility
        exchangePoints = team.calculatedData.teleopExchangeAbility
        drivingAbility = team.calculatedData.avgDrivingAbility
        climb = (team.calculatedData.avgNumRobotsLifted * 30) * (team.calculatedData.activeLiftClimbPercentage + team.calculatedData.soloClimbPercentage + team.calculatedData.assistedClimbPercentage + team.calculatedData.activeAssistClimbPercentage)
        return (drivingAbility + exchangePoints + autoPoints + switchPoints)

    #HEAVY PREDICTIONS AND ABILITIES - I'm in for a world of hurt

    def predictedScoreForAllianceAuto(self, match, allianceIsRed):
        autoRun = 5 * self.predictedAutoRunForAlliance(match, allianceIsRed)
        switch = 2 * self.predictedSwitchAuto(match, allianceIsRed)
        scale = 2 * self.predictedScaleAuto(match, allianceIsRed)
        scalePoints = (self.predictedScalePointsAuto(match, allianceIsRed) / utils.convertIdentity(self.predictedScalePointsAuto(match, allianceIsRed) + self.predictedScalePointsAuto(match, not allianceIsRed), 1.0, 0.0)) * min(30, self.predictedScalePointsAuto(match, allianceIsRed) + self.predictedScalePointsAuto(match, not allianceIsRed))
        switchPoints = self.predictedSwitchPointsAuto(match, allianceIsRed)
        return autoRun + switch + scale + scalePoints + switchPoints

    def getPredictedTeleopScoreForAlliance(self, match, allianceIsRed):
        predictedAllianceSwitchScore = min(155, (self.getTeleopAllianceSwitchAbilityForAlliance(match, allianceIsRed) - self.getTeleopOpponentSwitchAbilityForAlliance(match, not allianceIsRed)))
        predictedScaleScore = min(155, (self.getTeleopScaleAbilityForAlliance(match, allianceIsRed)))
        return predictedScaleScore + predictedAllianceSwitchScore + self.getTeleopExchangeAbilityForAlliance(match, allianceIsRed)

    def getPredictedScoreForAlliance(self, match, allianceIsRed):
        return self.getPredictedTeleopScoreForAlliance(match, allianceIsRed) + self.predictedScoreForAllianceAuto(match, allianceIsRed) + self.predictedFaceTheBoss(match, allianceIsRed)

    def drivingAbilityForTeam(self, team):
        agility = (0.45 * utils.convertNoneToIdentity(team.calculatedData.RScoreAgility, 0.0)) * 10
        speed = (0.45 * utils.convertNoneToIdentity(team.calculatedData.RScoreSpeed, 0.0)) * 10
        defense = (0.10 * utils.convertNoneToIdentity(team.calculatedData.RScoreDefense, 0.0)) * 10
        return agility + speed + defense

    #SEEDING - How each team seeds in the competition

    def cumulativeParkAndClimbPointsForTeam(self, team):
        parkPoints = (team.calculatedData.totalNumParks or 0) * 5
        climbPoints = (team.calculatedData.climbPercentage or 0) * len(self.su.getCompletedTIMDsForTeam(team)) * 30
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
        return [lambda t: self.predictedNumRPsForTeam(t), lambda t: self.cumulativeParkAndClimbPointsForTeam(t)]

    def actualNumberOfRPs(self, team):
        return self.getAverageForDataFunctionForTeam(team, lambda tm: tm.calculatedData.numRPs)

    def teamsSortedByRetrievalFunctions(self, retrievalFunctions):
        return sorted(self.cachedComp.teamsWithMatchesCompleted, key = lambda t: (retrievalFunctions[0](t) or 0, retrievalFunctions[1](t) or 0), reverse = True)

    def getTeamSeed(self, team):
        return int(filter(lambda x: int(x[1]) == team.number, self.cachedComp.actualSeedings)[0][0])

    def getTeamRPsFromTBA(self, team):
        return filter(lambda x: int(x[1]) == team.number, self.cachedComp.actualSeedings)[0][2]

    def RPsGainedFromMatchForAlliance(self, allianceIsRed, match):
        win = (1 if match.redScore == match.blueScore else 2 * (match.redScore > match.blueScore)) if allianceIsRed else (1 if match.redScore == match.blueScore else 2 * (match.blueScore > match.redScore))
        ftb = (1 if match.redDidFaceBoss else 0) if allianceIsRed else (1 if match.blueDidFaceBoss else 0)
        autoQuest = (1 if match.redDidAutoQuest else 0) if allianceIsRed else (1 if match.blueDidAutoQuest else 0)
        return win + ftb + autoQuest

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

    def rScoreTIMDParams(self):
        return [(lambda tm: tm.rankSpeed, self.cachedComp.speedTIMDZScores),
                     (lambda tm: tm.rankAgility, self.cachedComp.agilityTIMDZScores),
                     (lambda tm: tm.rankDefense, self.cachedComp.defenseTIMDZScores),
                     (lambda tm: tm.calculatedData.drivingAbility, self.cachedComp.drivingAbilityTIMDZScores)]   

    def cacheSecondTeamData(self):
        print('> Caching Second Team Data...')
        [self.rValuesForAverageFunctionForDict(func, dictionary) for (func, dictionary) in self.rScoreParams()]
        map(self.doSecondCachingForTeam, self.comp.teams)
        try:
            self.cachedComp.actualSeedings = self.TBAC.makeEventRankingsRequest()
        except KeyboardInterrupt:
            break
        except:
            self.cachedComp.actualSeedings = self.teamsSortedByRetrievalFunctions(self.getSeedingFunctions())
        self.cachedComp.predictedSeedings = self.teamsSortedByRetrievalFunctions(self.getPredictedSeedingFunctions())
        map(lambda t: Rscorecalcs(t, self), self.cachedComp.teamsWithMatchesCompleted)
        self.rValuesForAverageFunctionForDict(lambda t: t.calculatedData.avgDrivingAbility, self.cachedComp.drivingAbilityZScores)

    def doCachingForTeam(self, team):
        try:
            cachedData = self.cachedTeamDatas[team.number]
        except KeyboardInterrupt:
            break
        except:
            self.cachedTeamDatas[team.number] = cache.CachedTeamData(**{'teamNumber': team.number})
            cachedData = self.cachedTeamDatas[team.number]
        cachedData.completedTIMDs = self.su.retrieveCompletedTIMDsForTeam(team)

    def doSecondCachingForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]

    def cacheTBAMatches(self):
        try:
            self.cachedComp.TBAMatches = filter(lambda m: m['comp_level'] == 'qm', self.TBAC.makeEventMatchesRequest())
        except KeyboardInterrupt:
            break
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

    def doThirdCalculationsForTeam(self, team):
        if len(self.su.getCompletedMatchesForTeam(team)):
            thirdCalculationDict(team, self)
            print('> Completed third calculations for team ' + str(team.number))

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

    def setPointsPerCubes(self):
        print('> Setting points per cubes')
        self.pointsPerAllianceSwitchCube = self.getPointsPerAllianceSwitchCube()
        print('> AllianceSwitch - ' + str(self.pointsPerAllianceSwitchCube))
        self.pointsPerOpponentSwitchCube = self.getPointsPerOpponentSwitchCube()
        print('> OpponentSwitch - ' + str(self.pointsPerOpponentSwitchCube))
        self.pointsPerScaleCube = self.getPointsPerScaleCube()
        print('> Scale - ' + str(self.pointsPerScaleCube))

    def writeCalculationDiagnostic(self, time):
        with open('./diagnostics.txt', 'a') as file:
            file.write('Time:' + str(time) + '   TIMDs:' + str(len(self.su.getCompletedTIMDsInCompetition())) + '\n')
            file.close()

    def doCalculations(self, PBC):
        isData = len(self.su.getCompletedTIMDsInCompetition()) > 0
        if isData:
            startTime = time.time() #Gets time to later calculate time for a server cycle...
            self.cacheTBAMatches()
            #threads = [] #Creates an empty list for timds accessible in multiple processes (manager.list)
            #manager = multiprocessing.Manager()
            #calculatedTIMDs = manager.list()
            for timd in self.comp.TIMDs:
                #Does TIMD calculations to each TIMD in the competition, and puts the process into a list
                #the calculation results get put into
                #thread = FirstTIMDProcess(timd, calculatedTIMDs, self)
                #threads.append(thread)
                #thread.start()
                if not self.su.timdIsCompleted(timd):
                    print('> TIMD is not complete for team ' + str(timd.teamNumber) + ' in match ' + str(timd.matchNumber))
                    self.calcTIMDs.append(timd)
                else:
                    print('> Beginning first calculations for team ' + str(timd.teamNumber) + ' in match ' + str(timd.matchNumber))
                    TIMDCalcDict(timd, self)
                    self.calcTIMDs.append(timd)
                time.sleep(.01)
            #The main function does not continue until all of the TIMD processes are done (join)
            #map(lambda t: t.join(), threads)
            #Converts the shared list into a normal list            
            self.comp.TIMDs = self.calcTIMDs
            self.setPointsPerCubes()
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
            self.writeCalculationDiagnostic(endTime - startTime)
        else:
            print('> No calculations to do...')