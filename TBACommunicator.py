#Last Updated: 1/14/18
import requests
import json
import utils

class TBACommunicator(object):
	'''docstring for TBACommunicator'''
	def __init__(self):
		super(TBACommunicator, self).__init__()
		self.code = 'new'
		self.year = 2017
		self.key = str(self.year) + self.code
		self.authCode = 'erssexII0ARbu0mOasscljFGkq0zsreIBbzpnERZYrKV397fzoOTM7607SZzYjo8'
		self.basicURL = 'http://www.thebluealliance.com/api/v3/'
		self.headerKey = 'X-TBA-App-Id'
		self.headerValue = 'blm:server1678:004'
		self.authHeaderKey = 'X-TBA-Auth-Key'

	def makeRequest(self, url):
		return utils.makeASCIIFromJSON(requests.get(url, headers = {self.headerKey: self.headerValue, self.authHeaderKey: self.authCode}).json())

	# Makes request with additional headers, sends back status code, sends back return headers if requested
	def makeAdvancedRequest(self, url, headers, shouldReturnHeaders):
		headersDict = {self.headerKey: self.headerValue, self.authHeaderKey: self.authCode}
		headersDict.update(headers)
		r = requests.get(url, headers = headersDict)
		if r.status_code == 200:
			responseData = utils.makeASCIIFromJSON(r.json())
		else:
			return [r.status_code, None, None]
		return [r.status_code, r.headers, responseData] if shouldReturnHeaders else [r.status_code, None, responseData]

	def makeScheduleUpdaterRequest(self, matchNum, headers):
		url = self.basicURL + 'match/' + str(self.key) + '_qm' + str(matchNum)
		return self.makeAdvancedRequest(url, headers, True)

	def makeEventKeyRequestURL(self, key):
		return self.basicURL + 'event/' + self.key + '/' + key 

	def makeEventTeamsRequest(self):
		return self.makeRequest(self.makeEventKeyRequestURL('teams'))

	def makeTeamMediaRequest(self, teamKey):
		return self.makeRequest(self.basicURL + 'team/' + teamKey + '/media/' + str(self.year))

	def makeEventRankingsRequest(self):
		return self.makeRequest(self.makeEventKeyRequestURL('rankings'))[1:]

	def makeEventMatchesRequest(self):
		return self.makeRequest(self.makeEventKeyRequestURL('matches'))

	def makeSingleMatchRequest(self, matchNum):
		url = self.basicURL + 'match/' + str(self.key) + '_qm' + str(matchNum)
		return utils.makeASCIIFromJSON(self.makeRequest(url))

	def TBAIsBehind(self, matches):
		TBACompletedMatches = len(filter(lambda m: m['comp_level'] == 'qm' and m['score_breakdown'], self.makeEventMatchesRequest()))
		return abs(len(matches) - TBACompletedMatches) >= 3

	def getSurrogateTIMDsFromFirebase(self):
		surrogateTIMDs = {}
		for match in self.makeEventMatchesRequest():
			if match['alliances']['blue']['surrogate_team_keys'] != [] or match['alliances']['red']['surrogate_team_keys'] != []:
				surrogateTIMDs[str(match['match_number'])] = match['alliances']['blue']['surrogate_team_keys'] + match['alliances']['red']['surrogate_team_keys']
		for match in surrogateTIMDs:  
			for team in surrogateTIMDs[match]:
				surrogateTIMDs[match][surrogateTIMDs[match].index(team)] = team[3:]
		return surrogateTIMDs
