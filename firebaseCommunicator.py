#Last Updated: 2/11/18
import utils
import json
import datetime
import numpy as np
import pyrebase
from slackclient import SlackClient
import time

class PyrebaseCommunicator(object):
	'''docstring for PyrebaseCommunicator'''
	def __init__(self):
		super(PyrebaseCommunicator, self).__init__()
		self.JSONmatches = []
		self.JSONteams = []
		self.teamsList = []
		#self.url = 'scouting-2018-9023a'
		#self.url = 'scouting-2018-temp'
		#self.url = 'into-the-firebase-and-flames'
		#self.url = '1678-dev3-2016'
		self.url = 'scouting-2018-houston'
		config = {
			'apiKey': 'mykey',
			'authDomain': self.url + '.firebaseapp.com',
			'storageBucket': self.url + 'appspot.com',
			'databaseURL': 'https://' + self.url + '.firebaseio.com/'
		}
		app = pyrebase.initialize_app(config)
		self.firebase = app.database()
		self.fbStorage = app.storage()
		with open('SlackToken.csv', 'r') as file:
			self.slack = SlackClient(file.read())

	#Turns inputted team (class) object into dict and puts on firebase
	def updateFirebaseWithTeam(self, team):
		print(str(team.number) + ',',)
		teamDict = utils.makeDictFromTeam(team)
		self.teamsList.append(team.number)
		self.firebase.child('Teams').child(team.number).set(teamDict)

	#Turns inputted match (class) object into dict, condenses team numbers, and puts on firebase
	def updateFirebaseWithMatch(self, match):
		print(str(match.number) + ',',)
		matchDict = utils.makeDictFromMatch(match)
		matchDict['blueAllianceTeamNumbers'] = map(lambda n: int(n.replace('frc', '')), matchDict['blueAllianceTeamNumbers'])
		matchDict['redAllianceTeamNumbers'] = map(lambda n: int(n.replace('frc', '')), matchDict['redAllianceTeamNumbers'])
		self.firebase.child('Matches').child(match.number).set(matchDict)

	#Turns inputted TIMD (class) object into dict and puts on firebase
	def updateFirebaseWithTIMD(self, timd):
		timdDict = utils.makeDictFromTIMD(timd)
		print(str(timd.teamNumber) + 'Q' + str(timd.matchNumber) + ',' ,)
		self.firebase.child('TeamInMatchDatas').child(str(timd.teamNumber) + 'Q' + str(timd.matchNumber)).set(timdDict)

	def addCalculatedAutoRunsToFirebase(self, teams):
		dic = {7190: 0.9473684210526315, 7303: 0.7142857142857143, 3853: 0.8947368421052632, 1678: 1.0, 5997: 0.8666666666666667, 3472: 0.8823529411764706, 3473: 1.0, 6510: 1.0, 5654: 1.0, 2905: 0.8, 2840: 0.8333333333333334, 3481: 0.9411764705882353, 7067: 1.0, 4125: 0.75, 6424: 0.9230769230769231, 5663: 0.9411764705882353, 4513: 1.0, 1700: 0.6666666666666666, 604: 1.0, 5802: 1.0, 812: 1.0, 3501: 0.875, 4270: 1.0, 687: 1.0, 5700: 1.0, 5554: 1.0, 1011: 1.0, 7128: 0.9411764705882353, 6814: 0.8888888888888888, 3128: 0.875, 624: 1.0, 1723: 1.0, 6844: 0.8888888888888888, 1982: 1.0, 2367: 0.9333333333333333, 832: 1.0, 3140: 0.9285714285714286, 5104: 1.0, 968: 1.0, 6474: 0.9375, 971: 1.0, 1868: 0.8571428571428571, 5199: 1.0, 2403: 1.0, 3158: 1.0, 6871: 0.9166666666666666, 5849: 0.6842105263157895, 2980: 0.3333333333333333, 3164: 0.9444444444444444, 4061: 0.9166666666666666, 5726: 0.8823529411764706, 4576: 0.9166666666666666, 7137: 0.0, 1251: 0.9375, 3737: 1.0, 6377: 1.0, 5098: 1.0, 6891: 0.7777777777777778, 6508: 1.0, 3309: 0.95, 3310: 0.9444444444444444, 1648: 1.0, 1619: 0.9444444444444444, 4468: 0.8823529411764706, 6645: 0.65, 118: 1.0, 7134: 0.9}
		for team in teams:
			self.firebase.child('Teams').child(team.number).child('calculatedData').child('autoRunPercentage').set(dic[team.number])

	#Turns inputted CalculatedTeamData (class) object into dict and puts on firebase
	def addCalculatedTeamDataToFirebase(self, team):
		calculatedTeamDataDict = utils.makeDictFromCalculatedData(team.calculatedData)
		FBLocation = str(team.number) + '/calculatedData/'
		return {FBLocation : calculatedTeamDataDict}

	#Turns inputted Calculated TIMD (class) object into dict and puts on firebase
	def addCalculatedTIMDataToFirebase(self, timd):
		calculatedTIMDataDict = utils.makeDictFromCalculatedData(timd.calculatedData)
		FBLocation = str(timd.teamNumber) + 'Q' + str(timd.matchNumber) + '/calculatedData/'
		return {FBLocation : calculatedTIMDataDict}

	#Turns inputted CalculatedMatchData (class) object into dict and puts on firebase
	def addCalculatedMatchDataToFirebase(self, match):
		calculatedMatchDataDict = utils.makeDictFromCalculatedData(match.calculatedData)
		FBLocation = str(match.number) + '/calculatedData/'
		return {FBLocation : calculatedMatchDataDict}

	#Adds calculated data for each inputted team to firebase
	def addCalculatedTeamDatasToFirebase(self, teams):
		firebaseDict = {}
		[firebaseDict.update(self.addCalculatedTeamDataToFirebase(team)) for team in teams]
		print('> Uploading Teams to Firebase...')
		self.firebase.child('Teams').update(firebaseDict)

	#Adds calculated data for each inputted match to firebase
	def addCalculatedMatchDatasToFirebase(self, matches):
		firebaseDict = {}
		[firebaseDict.update(self.addCalculatedMatchDataToFirebase(match)) for match in matches]
		print('> Uploading Matches to Firebase...')
		self.firebase.child('Matches').update(firebaseDict)

	#Adds calculated data for each inputted TIMD to firebase
	def addCalculatedTIMDatasToFirebase(self, timds):
		firebaseDict = {}
		[firebaseDict.update(self.addCalculatedTIMDataToFirebase(timd)) for timd in timds]
		print('> Uploading TIMDs to Firebase...')
		self.firebase.child('TeamInMatchDatas').update(firebaseDict)

	#Puts all teams from local JSON list (probably from TBA) onto firebase
	def addTeamsToFirebase(self):
		print('\nDoing Teams...')
		map(lambda t: self.updateFirebaseWithTeam(utils.setDataForTeam(t)), self.JSONteams)
		self.firebase.child('TeamsList').set(self.teamsList)

	#Puts all qual matches from local JSON list (probably from TBA) onto firebase
	def addMatchesToFirebase(self):
		print('\nDoing Matches...')
		matches = filter(lambda m: m['comp_level'] == 'qm', self.JSONmatches)
		map(lambda m: self.updateFirebaseWithMatch(utils.setDataForMatch(m)), matches)

	def addSketchyMatchesToFirebase(self):
		newtonMatchDict = {1: {'blue': [1982, 5654, 1251], 'red': [687, 2403, 968]}, 2: {'blue': [7128, 3853, 3128], 'red': [1011, 1648, 6474]}, 3: {'blue': [2905, 971, 3309], 'red': [3472, 5802, 6377]}, 4: {'blue': [7303, 7190, 604], 'red': [3501, 5663, 4576]}, 5: {'blue': [4270, 5700, 4513], 'red': [6871, 3737, 4468]}, 6: {'blue': [5104, 3473, 2367], 'red': [2840, 5849, 6814]}, 7: {'blue': [6510, 5554, 1678], 'red': [832, 6645, 7067]}, 8: {'blue': [6508, 624, 7137], 'red': [118, 5098, 5726]}, 9: {'blue': [5997, 3140, 2980], 'red': [3158, 3481, 4125]}, 10: {'blue': [4061, 3164, 7134], 'red': [1619, 6424, 6844]}, 11: {'blue': [1868, 812, 1723], 'red': [3310, 1700, 5199]}, 12: {'blue': [2905, 5849, 7067], 'red': [6891, 1982, 7303]}, 13: {'blue': [2403, 6871, 1648], 'red': [5554, 4576, 971]}, 14: {'blue': [7128, 3309, 5726], 'red': [2840, 5104, 1678]}, 15: {'blue': [3158, 118, 6474], 'red': [4061, 3481, 3501]}, 16: {'blue': [4513, 3310, 5654], 'red': [4270, 1619, 5098]}, 17: {'blue': [6377, 4125, 6814], 'red': [1723, 968, 1011]}, 18: {'blue': [2367, 3140, 7190], 'red': [5700, 3472, 1700]}, 19: {'blue': [687, 832, 5663], 'red': [3164, 5997, 7137]}, 20: {'blue': [6508, 3853, 3737], 'red': [6844, 6510, 812]}, 21: {'blue': [1868, 2980, 3128], 'red': [3473, 7134, 624]}, 22: {'blue': [5802, 1251, 6645], 'red': [6424, 4468, 604]}, 23: {'blue': [6474, 6891, 5654], 'red': [4576, 1723, 5199]}, 24: {'blue': [3501, 687, 1619], 'red': [7067, 6871, 2367]}, 25: {'blue': [3158, 2403, 1700], 'red': [6508, 2905, 4270]}, 26: {'blue': [5098, 1011, 3472], 'red': [812, 832, 5997]}, 27: {'blue': [1982, 3473, 3310], 'red': [604, 118, 6510]}, 28: {'blue': [3853, 5802, 3481], 'red': [5554, 7134, 5104]}, 29: {'blue': [6814, 968, 6645], 'red': [971, 5726, 7190]}, 30: {'blue': [624, 6424, 5663], 'red': [5700, 7128, 6891]}, 31: {'blue': [4125, 1678, 1251], 'red': [3737, 7303, 1868]}, 32: {'blue': [3140, 2840, 4468], 'red': [2980, 3164, 6377]}, 33: {'blue': [5199, 6844, 5849], 'red': [3309, 4513, 3128]}, 34: {'blue': [7137, 7067, 4270], 'red': [1648, 4061, 5802]}, 35: {'blue': [624, 6814, 6891], 'red': [2403, 5997, 1619]}, 36: {'blue': [687, 6645, 4576], 'red': [5700, 3481, 6508]}, 37: {'blue': [4468, 3472, 968], 'red': [6424, 2840, 5098]}, 38: {'blue': [604, 1868, 5726], 'red': [6871, 2980, 971]}, 39: {'blue': [2905, 6474, 7128], 'red': [7190, 812, 4513]}, 40: {'blue': [5849, 6510, 7134], 'red': [3158, 6377, 5663]}, 41: {'blue': [118, 3309, 5104], 'red': [3737, 5654, 3164]}, 42: {'blue': [1251, 5554, 1011], 'red': [1700, 3501, 1982]}, 43: {'blue': [6844, 1648, 3473], 'red': [3140, 1723, 4125]}, 44: {'blue': [832, 4061, 7303], 'red': [3853, 2367, 5199]}, 45: {'blue': [1678, 3310, 2403], 'red': [7137, 3128, 5700]}, 46: {'blue': [4468, 812, 5849], 'red': [5654, 624, 971]}, 47: {'blue': [118, 6891, 4513], 'red': [2980, 3472, 5554]}, 48: {'blue': [1700, 2840, 5802], 'red': [6474, 3737, 687]}, 49: {'blue': [2367, 5726, 7303], 'red': [6844, 4270, 3158]}, 50: {'blue': [6814, 6510, 1648], 'red': [5098, 3501, 1868]}, 51: {'blue': [5199, 7128, 7137], 'red': [1619, 6377, 7067]}, 52: {'blue': [3164, 6508, 4125], 'red': [3128, 6871, 3310]}, 53: {'blue': [5104, 604, 968], 'red': [832, 7134, 3140]}, 54: {'blue': [5663, 1011, 3473], 'red': [3481, 6645, 2905]}, 55: {'blue': [1723, 1982, 6424], 'red': [5997, 1678, 3853]}, 56: {'blue': [3309, 4061, 5098], 'red': [7190, 4576, 1251]}, 57: {'blue': [6377, 6844, 624], 'red': [6814, 5554, 687]}, 58: {'blue': [971, 7303, 1619], 'red': [3128, 6474, 3140]}, 59: {'blue': [5726, 1700, 6510], 'red': [3481, 5654, 1648]}, 60: {'blue': [604, 3737, 6645], 'red': [2905, 7137, 1723]}, 61: {'blue': [2840, 4125, 832], 'red': [5700, 4061, 2403]}, 62: {'blue': [6871, 7190, 5997], 'red': [3853, 118, 5849]}, 63: {'blue': [4513, 2367, 1011], 'red': [4576, 6424, 1678]}, 64: {'blue': [968, 3501, 6891], 'red': [3164, 5802, 3310]}, 65: {'blue': [7128, 3472, 6508], 'red': [1251, 5199, 7134]}, 66: {'blue': [7067, 4468, 3158], 'red': [3473, 3309, 1868]}, 67: {'blue': [812, 2980, 1982], 'red': [5663, 5104, 4270]}, 68: {'blue': [3737, 1011, 4061], 'red': [3140, 5849, 624]}, 69: {'blue': [7303, 1700, 3481], 'red': [2403, 3164, 4513]}, 70: {'blue': [1619, 4576, 2905], 'red': [968, 6844, 118]}, 71: {'blue': [1678, 832, 6814], 'red': [5802, 6508, 4468]}, 72: {'blue': [971, 4270, 5997], 'red': [3473, 5700, 3501]}, 73: {'blue': [4125, 5554, 2367], 'red': [5654, 7128, 604]}, 74: {'blue': [6424, 5199, 3309], 'red': [3310, 2980, 687]}, 75: {'blue': [7134, 3158, 6871], 'red': [6645, 5098, 812]}, 76: {'blue': [6510, 7137, 3853], 'red': [6891, 1251, 2840]}, 77: {'blue': [1868, 7190, 6377], 'red': [1648, 1982, 5104]}, 78: {'blue': [5726, 3128, 3472], 'red': [5663, 7067, 1723]}, 79: {'blue': [5849, 4270, 5554], 'red': [6474, 6508, 6424]}, 80: {'blue': [1678, 3473, 968], 'red': [624, 6871, 1700]}, 81: {'blue': [3481, 812, 7137], 'red': [6814, 7303, 3309]}, 82: {'blue': [971, 3158, 1982], 'red': [3737, 832, 7128]}, 83: {'blue': [2403, 5098, 5802], 'red': [5199, 118, 3140]}, 84: {'blue': [5997, 1251, 3310], 'red': [5726, 6474, 6377]}, 85: {'blue': [4576, 5700, 5654], 'red': [7067, 3853, 2980]}, 86: {'blue': [3128, 5104, 2905], 'red': [6510, 687, 4061]}, 87: {'blue': [1011, 604, 6844], 'red': [4468, 6891, 7190]}, 88: {'blue': [1648, 1868, 3164], 'red': [6645, 2367, 3472]}, 89: {'blue': [3501, 1723, 2840], 'red': [7134, 4513, 1619]}, 90: {'blue': [5098, 5663, 1700], 'red': [3853, 4125, 3309]}, 91: {'blue': [5654, 3140, 6871], 'red': [1251, 2905, 6424]}, 92: {'blue': [5199, 6814, 3128], 'red': [604, 3158, 5554]}, 93: {'blue': [5997, 7067, 3737], 'red': [2367, 968, 6508]}, 94: {'blue': [687, 6377, 812], 'red': [6891, 1678, 4061]}, 95: {'blue': [2980, 3501, 6844], 'red': [6645, 2403, 7128]}, 96: {'blue': [7134, 4468, 6474], 'red': [7137, 4125, 1982]}, 97: {'blue': [3472, 4576, 3164], 'red': [5849, 5726, 3473]}, 98: {'blue': [5802, 1619, 5700], 'red': [1011, 1868, 6510]}, 99: {'blue': [3310, 1648, 118], 'red': [7303, 5663, 2840]}, 100: {'blue': [1723, 624, 3481], 'red': [4270, 7190, 832]}, 101: {'blue': [4513, 6844, 7067], 'red': [5104, 971, 1251]}, 102: {'blue': [7128, 5997, 4576], 'red': [1700, 3128, 4468]}, 103: {'blue': [6474, 6510, 6871], 'red': [3309, 2367, 2403]}, 104: {'blue': [1678, 5849, 2980], 'red': [968, 1619, 1648]}, 105: {'blue': [6377, 6424, 832], 'red': [812, 5726, 3501]}, 106: {'blue': [5098, 1723, 5700], 'red': [5554, 2905, 3164]}, 107: {'blue': [4061, 3310, 3853], 'red': [3472, 6814, 3737]}, 108: {'blue': [6645, 5104, 624], 'red': [4125, 5199, 7303]}, 109: {'blue': [5663, 1868, 6891], 'red': [3140, 4513, 6508]}, 110: {'blue': [7190, 3473, 3158], 'red': [5654, 7137, 5802]}, 111: {'blue': [4270, 687, 118], 'red': [1011, 971, 7134]}}
		for number, match in newtonMatchDict.items():
			matchDict = {}
			matchDict['blueAllianceTeamNumbers'] = match['blue']
			matchDict['redAllianceTeamNumbers'] = match['red']
			matchDict['number'] = number
			self.firebase.child('Matches').child(number).set(matchDict)

	def addTIMDsToFirebase(self, matches):
		#gets all team numbers in a given match and updates firebase with the corresponding TIMD
		print('\nDoing TIMDs...')
		timdFunc = lambda t, m: self.updateFirebaseWithTIMD(utils.makeTIMDFromTeamNumberAndMatchNumber(t, m.number))
		addTIMD = lambda m: map(lambda t: timdFunc(t, m), m.redAllianceTeamNumbers + m.blueAllianceTeamNumbers)
		map(addTIMD, matches)

	def addSlackProfilesToFirebase(self):
		#Adds all of the slack profiles to the firebase
		print('\nAdding slack profiles\n')
		data = self.slack.api_call('users.list')
		for member in data['members']:
			if not member['deleted'] and not (member['is_bot'] or member['name'] == 'slackbot'):
				ID = member['id']
				tag = member['profile']['display_name_normalized']
				name = member['profile']['real_name_normalized']
				if tag == '':
					tag = name
				print('Added the lovely person known as ' + name)
				self.firebase.child('slackProfiles/'+str(ID)).set({'name':name,'tag':tag})

	#Puts all of firebase onto a local JSON
	def cacheFirebase(self):
		try:
			data = dict(self.firebase.get().val())
			now = str(datetime.datetime.now())
			with open('./CachedFirebases/' + now + '.json', 'w+') as f:
				json.dump(data, f)
		except KeyboardInterrupt:
			return
		except:
			pass

	#Empties everything from firebase
	def wipeDatabase(self):
		map(utils.printWarningForSeconds, range(10, 0, -1))
		print('\nWARNING: Wiping Firebase...')
		self.firebase.remove()

	def getPythonObjectForFirebaseDataAtLocation(self, location):
		return utils.makeASCIIFromJSON(self.firebase.child(location).get().val())

	#Stores inputted file (data export) on firebase
	def sendExport(self, fileName):
		now = str(datetime.datetime.now())
		filePath = './' + fileName
		self.fbStorage.child('Exports').child(fileName).put(filePath)

	#Puts current match number on firebase as 1
	def addSingleKeysToFirebase(self):
		self.firebase.child('currentMatchNum').set(1)
		self.firebase.child('cycleCounter').set(0)
