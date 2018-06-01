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
        #Dictionary for super keys that are checked from data on TBA
        #Format is {key : [allianceColor, TBA key, Is it in score_breakdown?]}
        self.TBACheckedSuperKeys = {'blueDidFaceBoss' : ['blue', 'faceTheBossRankingPoint', True], 
                                    'redDidFaceBoss' : ['red', 'faceTheBossRankingPoint', True], 
                                    'blueDidAutoQuest' : ['blue', 'autoQuestRankingPoint', True], 
                                    'redDidAutoQuest' : ['red', 'autoQuestRankingPoint', True],
                                    'blueScore' : ['blue', 'score', False],
                                    'redScore' : ['red', 'score', False],
                                    }
        self.ourTeamNum = 1678
        self.su = SchemaUtils(self.comp, self)
        self.cachedTeamDatas = {}
        self.averageTeam = DataModel.Team()
        self.averageTeam.number = -1
        self.averageTeam.name = 'Average Team'
        self.calcTIMDs = []
        self.pointsPerScaleCube = 0.0
        self.pointsPerAllianceSwitchCube = 0.0
        self.pointsPerOpponentSwitchCube = 0.0
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

    #CALCULATED TEAM DATA

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
            return
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
            return
        except:
            numerator = 0.0
            denominator = 0.0
        return numerator / denominator if denominator != 0 else 0.0

    def getAvgNumCompletedTIMDsForTeamsOnAlliance(self, match, allianceIsRed):
        alliance = self.su.getAllianceForMatch(match, allianceIsRed)
        return sum(map(lambda t: len(self.su.getCompletedTIMDsForTeam(t)), alliance))

    #NON-SYSTEMATIC TEAM CALCULATIONS

    def getVaultTimeScore(self, team):
        vaultTime = team.calculatedData.avgAllVaultTime
        ppvc = self.getPointsPerVaultCube()
        try:
            return (9.0 / vaultTime * ppvc)
        except:
            return 0.0

    def autoRunBackup(self, team):
        team = 'frc' + str(team.number)
        matches = filter(lambda m: team in (m['alliances']['blue']['team_keys'] + m['alliances']['red']['team_keys']), self.cachedComp.TBAMatches)
        autoRuns = []
        for match in matches:
            if match['score_breakdown']:
                allianceColor = 'blue' if team in match['alliances']['blue']['team_keys'] else 'red'
                robotNum = (match['alliances'][allianceColor]['team_keys'].index(team)) + 1
                autoRuns += [True if match['score_breakdown'][allianceColor]['autoRobot' + str(robotNum)]  == 'AutoRun' else False]
        if autoRuns:
            return utils.avg(autoRuns)
        else:
            return 0

    def getTotalCubesPlaced(self, team, lfm):
        return float(float(team.calculatedData.lfmAvgNumCubesPlacedAuto) + float(team.calculatedData.lfmAvgNumCubesPlacedTele)) if lfm else float(float(team.calculatedData.avgNumCubesPlacedAuto) + float(team.calculatedData.avgNumCubesPlacedTele))

    def getMaxScaleCubes(self, team, lfm):
        return (max([(timd.calculatedData.numScaleSuccessTele + timd.calculatedData.numScaleSuccessAuto) for timd in self.su.getRecentTIMDsForTeam(team)])) if lfm else (max([(timd.calculatedData.numScaleSuccessTele + timd.calculatedData.numScaleSuccessAuto) for timd in self.su.getCompletedTIMDsForTeam(team)]))

    def getMaxExchangeCubes(self, team, lfm):
        return (max([(timd.numExchangeInput) for timd in self.su.getRecentTIMDsForTeam(team)])) if lfm else (max([(timd.numExchangeInput) for timd in self.su.getCompletedTIMDsForTeam(team)]))

    def getPercentageForClimbType(self, team, climbType, lfm):
        return utils.avg([climb[1]['didSucceed'] if climb[0] == climbType else False for x in self.su.getRecentTIMDsForTeam(team) for attempt in x.climb for climb in attempt.items()]) if lfm else utils.avg([climb[1]['didSucceed'] if climb[0] == climbType else False for x in self.su.getCompletedTIMDsForTeam(team) for attempt in x.climb for climb in attempt.items()])

    def getPercentageForActiveClimbType(self, team, didClimb, liftType, lfm):
        return utils.avg([climb[1]['didSucceed'] if climb[0] == 'activeLift' and climb[1].get('didClimb', None) == didClimb and climb[1].get('partnerLiftType', None) == liftType else False for x in self.su.getRecentTIMDsForTeam(team) for attempt in x.climb for climb in attempt.items()]) if lfm else utils.avg([climb[1]['didSucceed'] if climb[0] == 'activeLift' and climb[1].get('didClimb', None) == didClimb and climb[1].get('partnerLiftType', None) == liftType else False for x in self.su.getCompletedTIMDsForTeam(team) for attempt in x.climb for climb in attempt.items()])

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

    #TEAM IN MATCH CALCULATIONS

    def parkBackup(self, team, matches, matchNum, timd):
        team = 'frc' + str(team.number)
        match = filter(lambda match: match['match_number'] == matchNum and match['comp_level'] == 'qm', matches)[0]
        if match['score_breakdown']:
            allianceColor = 'blue' if team in match['alliances']['blue']['team_keys'] else 'red'
            robotNum = (match['alliances'][allianceColor]['team_keys'].index(team)) + 1
            didPark = (match['score_breakdown'][allianceColor]['endgameRobot' + str(robotNum)]  == 'Parking')
        if didPark == True and timd.climb:
            timd.climb = None
        return didPark

    def getAvgVaultTime(self, vault):
        if vault != []:
            times = []
            for cycle in vault:
                try:
                    if cycle['cubes'] > 3:
                        times.append((cycle['time'] / float(cycle['cubes'])))
                except:
                    pass
            if times != []:
                return (utils.avg(times) * 9.0)

    def scaleCubesByCertainTime(self, timd, time):
        scaleAttempts = timd.scaleAttemptAuto + timd.scaleAttemptTele
        return len([attempt['didSucceed'] for attempt in scaleAttempts if attempt['didSucceed'] == True and attempt['endTime'] < time])

    def switchOwnership(self, timd):
        match = filter(lambda m: m['match_number'] == timd.matchNumber and m['comp_level'] == 'qm', self.cachedComp.TBAMatches)[0]
        allianceColor = 'red' if ('frc' + str(timd.teamNumber)) in match['alliances']['red']['team_keys'] else 'blue'
        try:
            return (match['score_breakdown'][allianceColor]['autoSwitchOwnershipSec'] + match['score_breakdown'][allianceColor]['teleopSwitchOwnershipSec'])
        except:
            return 0

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
        if times != []:
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
        return True if (team.calculatedData.avgNumGroundIntakeTele) > 0 else False

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

    #TBA INVOLVEMENT FOR SCORE BREAKDOWN

    def getPointsEarnedOnScaleForAllianceAuto(self, match, allianceIsRed):
        match = filter(lambda m: m['match_number'] == match.number, self.cachedComp.TBAMatches)[0]
        return match['score_breakdown']['red']['autoScaleOwnershipSec'] if allianceIsRed else match['score_breakdown']['blue']['autoScaleOwnershipSec']

    def getPointsEarnedOnScaleForAllianceTele(self, match, allianceIsRed):
        match = filter(lambda m: m['match_number'] == match.number, self.cachedComp.TBAMatches)[0]
        return match['score_breakdown']['red']['teleopScaleOwnershipSec'] if allianceIsRed else match['score_breakdown']['blue']['teleopScaleOwnershipSec']

    def getPointsEarnedOnAllianceSwitchForAllianceAuto(self, match, allianceIsRed):
        match = filter(lambda m: m['match_number'] == match.number, self.cachedComp.TBAMatches)[0]
        return match['score_breakdown']['red']['autoSwitchOwnershipSec'] if allianceIsRed else match['score_breakdown']['blue']['autoSwitchOwnershipSec']

    def getPointsEarnedOnAllianceSwitchForAllianceTele(self, match, allianceIsRed):
        match = filter(lambda m: m['match_number'] == match.number, self.cachedComp.TBAMatches)[0]
        return match['score_breakdown']['red']['teleopSwitchOwnershipSec'] if allianceIsRed else match['score_breakdown']['blue']['teleopSwitchOwnershipSec']

    #PREDICTIONS

    def predictedParkForTeam(self, team):
        try:
            return (float(team.calculatedData.totalNumParks) / (len(self.su.getCompletedTIMDsForTeam(team)) - team.calculatedData.numSuccessfulClimbs))
        except:
            return 0.0

    def predictedParkForAlliance(self, match, allianceIsRed):
        parks = utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.predictedPark for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])], 0.0)
        if parks:
            return reduce(lambda x, y: x + y, parks)
        return 0.0

    def levitateProbabilityForAlliance(self, match, allianceIsRed):
        return 1 - reduce(lambda x, y: x * y, [1 - x for x in utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.didThreeExchangeInputPercentage for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])], 0.0)])

    def predictedAutoRunForAlliance(self, match, allianceIsRed):
        return reduce(lambda x, y: x * y, utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.autoRunPercentage for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])], 1.0))

    def predictedFaceTheBossForTeamInMatch(self, match, team):
        climbPercentages = {'sc' : team.calculatedData.soloClimbPercentage, 'aa' : team.calculatedData.activeAssistClimbPercentage, 'al' : team.calculatedData.activeLiftClimbPercentage, 'ancl' : team.calculatedData.activeNoClimbLiftClimbPercentage, 'ac' : team.calculatedData.assistedClimbPercentage}
        return (max(climbPercentages, key = (lambda k: climbPercentages[k])), climbPercentages[max(climbPercentages, key = (lambda key: climbPercentages[key]))]) 

    def predictedFaceTheBoss(self, match, allianceIsRed):
        climbPercentages = [self.predictedFaceTheBossForTeamInMatch(match, team) for team in self.su.getAllianceForMatch(match, allianceIsRed)]
        a = [(x, y) for x,y in climbPercentages if x == 'sc' or x == 'ac']
        b = [(x, y) for x,y in climbPercentages if x == 'aa' or x == 'al' or x == 'ancl']
        try:
            highest = float(sorted([y for x,y in a])[-1]) or 0.0
            second = float(sorted([y for x,y in a])[-2]) or 0.0
            solos = highest * second
            active = float(max([y for x,y in b] or [0.0]))
            return max(solos, active)
        except:
            return 0.0

    def predictedScaleAuto(self, match, allianceIsRed):
        return max(utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.scaleSuccessPercentageAuto for teamNumber in (match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers)], 0.0))
    
    def predictedSwitchAuto(self, match, allianceIsRed):
        return max(utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.allianceSwitchSuccessPercentageAuto for teamNumber in ([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0])], 0.0))

    def predictedScaleTimeAuto(self, match, allianceIsRed):
        return utils.convertNoneToIdentity((sorted([self.su.getTeamForNumber(teamNumber) for teamNumber in [match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0]], key = lambda tm: tm.calculatedData.scaleSuccessPercentageAuto)[-1]).calculatedData.avgTimeToOwnScaleAuto, 0.0)

    def predictedSwitchTimeAuto(self, match, allianceIsRed):
        return utils.convertNoneToIdentity((sorted([self.su.getTeamForNumber(teamNumber) for teamNumber in [match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers][0]], key = lambda tm: tm.calculatedData.allianceSwitchSuccessPercentageAuto)[-1]).calculatedData.avgTimeToOwnAllianceSwitchAuto, 0.0)

    def predictedTotalNumRPsForTeam(self, team):
        return sum([match.calculatedData.predictedRedRPs if team.number in match.redAllianceTeamNumbers else match.calculatedData.predictedBlueRPs for match in self.su.getCompletedMatchesForTeam(team)])

    def predictedNumRPsForTeam(self, team):
        rps = [match.calculatedData.predictedRedRPs if team.number in match.redAllianceTeamNumbers else match.calculatedData.predictedBlueRPs for match in self.su.getMatchesForTeam(team)]
        if rps:
            return utils.avg(rps)
        else:
            return 0

    def predictedRPsForAlliance(self, match, allianceIsRed):
        if match.calculatedData.actualRedRPs == None:
            return self.predictedWinRP(match, allianceIsRed) + self.predictedAutoQuestRP(match, allianceIsRed) + self.predictedFaceTheBossRP(match, allianceIsRed)
        else:
            return match.calculatedData.actualRedRPs if allianceIsRed else match.calculatedData.actualBlueRPs

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

    def predictedTotalEndgamePointsForAlliance(self, match, allianceIsRed):
        park = 5 * self.predictedParkForAlliance(match, allianceIsRed)
        climbPercentages = [self.predictedFaceTheBossForTeamInMatch(match, team) for team in self.su.getAllianceForMatch(match, allianceIsRed)]
        a = [(x, y) for x,y in climbPercentages if x == 'sc' or x == 'ac']
        b = [(x, y) for x,y in climbPercentages if x == 'aa' or x == 'al' or x == 'ancl']
        climb = max(([utils.convertNoneToIdentity(climb, 0.0) * 30.0 for ty, climb in a] + [utils.convertNoneToIdentity(climb, 0.0) * 60.0 for ty, climb in b]))
        endgame = min(90, ((30 * self.levitateProbabilityForAlliance(match, allianceIsRed)) + climb + park))
        return endgame

    #ABILITIES AND POINT CALCULATIONS

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
        return min(9, sum(utils.replaceFromNone([self.su.getTeamForNumber(teamNumber).calculatedData.avgNumExchangeInputTele for teamNumber in utils.extendList([match.redAllianceTeamNumbers if allianceIsRed else match.blueAllianceTeamNumbers])], 0.0))) * 5

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
        total = 2.0 * (team.calculatedData.avgNumCubesPlacedTele) 
        scale = 10.0 * (team.calculatedData.avgScaleCubesBy100s)
        speed = 1.0 * (team.calculatedData.RScoreSpeed)
        agile = 4.0 * (team.calculatedData.RScoreAgility)
        return (total + scale + speed + agile)

    def getSecondPickAbilityForTeam(self, team):
        total = 5.0 * (team.calculatedData.avgTotalCubesPlaced) 
        excha = 5.5 * (team.calculatedData.avgNumExchangeInputTele)
        oppSw = 5.0 * (team.calculatedData.avgOpponentSwitchCubesTele)
        alSwA = 1.5 * (team.calculatedData.avgAllianceSwitchCubesAuto)
        alSwT = 1.0 * (team.calculatedData.avgAllianceSwitchCubesTele)
        other = 6.0 * (team.calculatedData.avgTotalCubesPlaced - (team.calculatedData.avgNumExchangeInputTele + team.calculatedData.avgOpponentSwitchCubesTele + team.calculatedData.avgAllianceSwitchCubesTele))
        vTime = 5.0 * (team.calculatedData.vaultTimeScore)
        speed = 0.05 * (team.calculatedData.RScoreSpeed)
        agile = 0.3 * (team.calculatedData.RScoreAgility)
        return (total + excha + oppSw + alSwA + alSwT + other + vTime + speed + agile)

    #HEAVY PREDICTIONS AND ABILITIES

    def predictedScoreForAllianceAuto(self, match, allianceIsRed):
        autoRun = 15 * self.predictedAutoRunForAlliance(match, allianceIsRed)
        scalePoints = (self.predictedScalePointsAuto(match, allianceIsRed) / utils.convertIdentity(self.predictedScalePointsAuto(match, allianceIsRed) + self.predictedScalePointsAuto(match, not allianceIsRed), 1.0, 0.0)) * min(30, self.predictedScalePointsAuto(match, allianceIsRed) + self.predictedScalePointsAuto(match, not allianceIsRed))
        switchPoints = self.predictedSwitchPointsAuto(match, allianceIsRed)
        return autoRun + scalePoints + switchPoints

    def getPredictedScaleTeleopScoreForAlliance(self, match, allianceIsRed):
        predictedScaleScore = (self.getTeleopScaleAbilityForAlliance(match, allianceIsRed))
        predictedOpponentScaleScore = (self.getTeleopScaleAbilityForAlliance(match, not allianceIsRed))
        higherScore = True if predictedScaleScore > predictedOpponentScaleScore else False
        difference = 135 - (predictedScaleScore + predictedOpponentScaleScore)
        if difference > 0:
            if higherScore:
                predictedScaleScore += difference
        else:
            if not higherScore:
                predictedScaleScore += difference
        return predictedScaleScore

    def getPredictedAllianceSwitchTeleopScoreForAlliance(self, match, allianceIsRed):
        predictedAllianceSwitchScore = (self.getTeleopAllianceSwitchAbilityForAlliance(match, allianceIsRed))
        predictedOpponentAllianceSwitchScore = (self.getTeleopOpponentSwitchAbilityForAlliance(match, not allianceIsRed))
        higherScore = True if predictedAllianceSwitchScore > predictedOpponentAllianceSwitchScore else False
        difference = 135 - (predictedAllianceSwitchScore + predictedOpponentAllianceSwitchScore)
        if difference > 0:
            if higherScore:
                predictedAllianceSwitchScore += difference
        else:
            if not higherScore:
                predictedAllianceSwitchScore += difference
        return predictedAllianceSwitchScore

    def getPredictedTeleopScoreForAlliance(self, match, allianceIsRed):
        predictedAllianceSwitchScore = self.getPredictedAllianceSwitchTeleopScoreForAlliance(match, allianceIsRed)
        predictedScaleScore = self.getPredictedScaleTeleopScoreForAlliance(match, allianceIsRed)
        return utils.nullifyOutwardValue(predictedScaleScore) + utils.nullifyOutwardValue(predictedAllianceSwitchScore) + self.getTeleopExchangeAbilityForAlliance(match, allianceIsRed)

    def getPredictedScoreForAlliance(self, match, allianceIsRed):
        return self.getPredictedTeleopScoreForAlliance(match, allianceIsRed) + self.predictedScoreForAllianceAuto(match, allianceIsRed) + self.predictedTotalEndgamePointsForAlliance(match, allianceIsRed)

    def drivingAbilityForTeam(self, team):
        agile = 0.80 * (utils.convertNoneToIdentity(team.calculatedData.RScoreAgility, 0.0)) * 10
        speed = 0.20 * (utils.convertNoneToIdentity(team.calculatedData.RScoreSpeed, 0.0)) * 10
        defen = 0.00 * (utils.convertNoneToIdentity(team.calculatedData.RScoreDefense, 0.0)) * 10
        return agile + speed + defen

    def getAutoStandardDeviationForTeam(self, team):
        timds = self.su.getCompletedTIMDsForTeam(team)
        if timds:
            autoRun = np.std([tm.didMakeAutoRun for tm in timds]) * 5
            autoSwitch = np.std([tm.calculatedData.timeToOwnAllianceSwitchAuto for tm in timds]) * 2
            autoScale = np.std([tm.calculatedData.timeToOwnScaleAuto for tm in timds]) * 2
            return utils.sumStdDevs([autoRun, autoSwitch, autoScale])
        return 0.0

    def getAutoStandardDeviationForAlliance(self, alliance):
        return utils.sumStdDevs([self.getAutoStandardDeviationForTeam(team) for team in alliance])

    def getTeleopStandardDeviationForTeam(self, team):
        timds = self.su.getCompletedTIMDsForTeam(team)
        if timds:
            switch = np.std([tm.calculatedData.numAllianceSwitchSuccessTele for tm in timds]) * self.pointsPerAllianceSwitchCube
            scale = np.std([tm.calculatedData.numScaleSuccessTele for tm in timds]) * self.pointsPerScaleCube
            exchange = np.std([tm.numExchangeInput for tm in timds]) * 5
            climb = np.std([tm.calculatedData.didClimb for tm in timds]) * 30
            return utils.sumStdDevs([switch, scale, exchange, climb])
        return 0.0

    def getTeleopStandardDeviationForAlliance(self, alliance):
        return utils.sumStdDevs([self.getTeleopStandardDeviationForTeam(team) for team in alliance])

    def stdPredictedScoreForAlliance(self, match, allianceIsRed):
        alliance = self.su.getAllianceForMatch(match, allianceIsRed)
        autoStdDev = self.getAutoStandardDeviationForAlliance(alliance)
        teleopStdDev = self.getTeleopStandardDeviationForAlliance(alliance)
        return utils.sumStdDevs([autoStdDev, teleopStdDev])

    def winChanceForAlliance(self, match, allianceIsRed):
        predictedScore = match.calculatedData.predictedRedScore if allianceIsRed else match.calculatedData.predictedBlueScore
        opposingPredictedScore = match.calculatedData.predictedBlueScore if allianceIsRed else match.calculatedData.predictedRedScore
        sdPredictedScore = 5 * self.stdPredictedScoreForAlliance(match, allianceIsRed)
        sdOpposingPredictedScore = 5 * self.stdPredictedScoreForAlliance(match, not allianceIsRed)
        sampleSize = self.getAvgNumCompletedTIMDsForTeamsOnAlliance(match, allianceIsRed)
        opposingSampleSize = self.getAvgNumCompletedTIMDsForTeamsOnAlliance(match, not allianceIsRed)
        tscoreRPs = self.welchsTest(predictedScore,
                                       opposingPredictedScore,
                                       sdPredictedScore,
                                       sdOpposingPredictedScore,
                                       sampleSize,
                                       opposingSampleSize)
        df = self.getDF(sdPredictedScore, opposingPredictedScore, sampleSize, opposingSampleSize)
        winChance = stats.t.cdf(tscoreRPs, df)
        return winChance if not math.isnan(winChance) else 0

    #SEEDING

    def cumulativeParkAndClimbPointsForTeam(self, team):
        frcTeam = 'frc' + str(team.number)
        matches = filter(lambda match: frcTeam in match['alliances']['red']['team_keys'] or frcTeam in match['alliances']['blue']['team_keys'], self.cachedComp.TBAMatches) 
        cumulative = 0
        for match in matches:
            allianceColor = 'red' if frcTeam in match['alliances']['red']['team_keys'] else 'blue'
            try:
                cumulative += match['score_breakdown'][allianceColor]['endgamePoints']
            except:
                pass
        return cumulative

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
        rankForTeam = {team['team_key'] : team['rank'] for team in self.cachedComp.TBARankings}
        return rankForTeam[('frc' + str(team.number))]

    def getTeamRPsFromTBA(self, team):
        rankings = self.cachedComp.TBARankings
        rpsForTeam = {team['team_key'] : [team['extra_stats'][0], team['matches_played']] for team in rankings}
        totalRPs = rpsForTeam[('frc' + str(team.number))][0]
        return float(totalRPs) / float(rpsForTeam[('frc' + str(team.number))][1])

    def RPsGainedFromMatchForAlliance(self, allianceIsRed, match):
        win = (1 if match.redScore == match.blueScore else 2 * (match.redScore > match.blueScore)) if allianceIsRed else (1 if match.redScore == match.blueScore else 2 * (match.blueScore > match.redScore))
        ftb = (1 if match.redDidFaceBoss else 0) if allianceIsRed else (1 if match.blueDidFaceBoss else 0)
        autoQuest = (1 if match.redDidAutoQuest else 0) if allianceIsRed else (1 if match.blueDidAutoQuest else 0)
        return win + ftb + autoQuest

    def totalNumRPsForTeam(self, team):
        return sum([match.calculatedData.actualRedRPs if team.number in match.redAllianceTeamNumbers else match.calculatedData.actualBlueRPs for match in self.su.getCompletedMatchesForTeam(team)])
    
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
            self.cachedComp.actualSeedings = sorted({team['team_key'] : team['r'] for team in self.cachedComp.TBARankings}, key = lambda t: t)[::-1]
        except KeyboardInterrupt:
            return
        except:
            self.cachedComp.actualSeedings = self.teamsSortedByRetrievalFunctions(self.getSeedingFunctions())[::-1]
        self.cachedComp.predictedSeedings = self.teamsSortedByRetrievalFunctions(self.getPredictedSeedingFunctions())
        map(lambda t: Rscorecalcs(t, self), self.cachedComp.teamsWithMatchesCompleted)
        self.rValuesForAverageFunctionForDict(lambda t: t.calculatedData.avgDrivingAbility, self.cachedComp.drivingAbilityZScores)

    def doCachingForTeam(self, team):
        try:
            cachedData = self.cachedTeamDatas[team.number]
        except KeyboardInterrupt:
            return
        except:
            self.cachedTeamDatas[team.number] = cache.CachedTeamData(**{'teamNumber': team.number})
            cachedData = self.cachedTeamDatas[team.number]
        cachedData.completedTIMDs = self.su.retrieveCompletedTIMDsForTeam(team)

    def doSecondCachingForTeam(self, team):
        cachedData = self.cachedTeamDatas[team.number]

    def cacheTBAData(self):
        try:
            self.cachedComp.TBAMatches = filter(lambda m: m['comp_level'] == 'qm', self.TBAC.makeEventMatchesRequest())
            self.cachedComp.TBARankings = self.TBAC.makeEventRankingsRequest()
        except KeyboardInterrupt:
            return
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

    def checkEndgameSuperData(self, PBC):
        print('> Checking super data...')
        matches = PBC.firebase.child('Matches').get().val()
        for match in self.comp.matches:
            TBAMatch = filter(lambda m: m['match_number'] == match.number, self.cachedComp.TBAMatches)[0]
            try:
                for key, values in self.TBACheckedSuperKeys.items():
                    if values[2] == True:
                        matches[match.number][key] = TBAMatch['score_breakdown'][values[0]][values[1]]
                    else:
                        matches[match.number][key] = TBAMatch['alliances'][values[0]][values[1]]
            except:
                pass
        PBC.firebase.child('Matches').set(list(matches))
    
    def addTBAcode(self, PBC):
        PBC.firebase.child('TBAcode').set(self.TBAC.code)

    def writeCalculationDiagnostic(self, time):
        with open('./diagnostics.txt', 'a') as file:
            file.write('Time:' + str(time) + '   TIMDs:' + str(len(self.su.getCompletedTIMDsInCompetition())) + '\n')
            file.close()

    def doCalculations(self, PBC, isFull):
        isData = len(self.su.getCompletedTIMDsInCompetition()) > 0
        if isData:
            startTime = time.time() #Gets time to later calculate time for a server cycle...
            self.cacheTBAData()
            self.calcTIMDs = []
            for timd in self.comp.TIMDs:
                #Does calculations for each timd
                if not self.su.timdIsCompleted(timd):
                    print('> TIMD is not complete for team ' + str(timd.teamNumber) + ' in match ' + str(timd.matchNumber))
                    self.calcTIMDs.append(timd)
                else:
                    print('> Beginning first calculations for team ' + str(timd.teamNumber) + ' in match ' + str(timd.matchNumber))
                    TIMDCalcDict(timd, self)
                    self.calcTIMDs.append(timd)
            self.comp.TIMDs = self.calcTIMDs
            self.setPointsPerCubes()
            self.cacheFirstTeamData()
            self.doFirstTeamCalculations()
            self.cacheSecondTeamData()
            self.doMatchesCalculations()
            self.doSecondTeamCalculations()
            print('> Calculations finished, adding data to firebase')
            if isFull:
                PBC.addCalculatedTIMDatasToFirebase(self.su.getCompletedTIMDsInCompetition())
            else:
                PBC.addCalculatedTIMDatasToFirebase(self.su.getRecentCompletedTIMDsInCompetition())
            PBC.addCalculatedTeamDatasToFirebase(self.cachedComp.teamsWithMatchesCompleted)
            PBC.addCalculatedMatchDatasToFirebase(self.comp.matches)
            endTime = time.time()
            self.writeCalculationDiagnostic(endTime - startTime)
        else:
            print('> No calculations to do...')
