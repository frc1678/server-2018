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
		self.speedZScores = {-1 : 0}
		self.agilityZScores = {-1 : 0}
		self.defenseZScores = {-1 : 0}
		self.drivingAbilityZScores = {-1 : 0}
		self.predictedSeedings = []
		self.actualSeedings = []
		self.TBAMatches = {}
