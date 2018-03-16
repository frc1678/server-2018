#Last Updated: 1/20/17
class CachedTeamData(object):
	def __init__(self, teamNumber):
		super(CachedTeamData, self).__init__()
		self.number = teamNumber
		self.completedTIMDs = []

class CachedCompetitionData(object):
	def __init__(self):
		super(CachedCompetitionData, self).__init__()
		self.teamsWithMatchesCompleted = []
		self.speedZScores = {}
		self.agilityZScores = {}
		self.defenseZScores = {}
		self.drivingAbilityZScores = {}
		self.speedTIMDZScores = {-1 : 0}
		self.agilityTIMDZScores = {-1 : 0}
		self.defenseTIMDZScores = {-1 : 0}
		self.drivingAbilityTIMDZScores = {-1 : 0}
		self.predictedSeedings = []
		self.actualSeedings = []
		self.TBAMatches = {}
