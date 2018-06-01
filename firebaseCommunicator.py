import utils
import json
import datetime
import pyrebase
from slackclient import SlackClient

class PyrebaseCommunicator(object):
	'''docstring for PyrebaseCommunicator'''
	def __init__(self):
		super(PyrebaseCommunicator, self).__init__()
		self.JSONmatches = []
		self.JSONteams = []
		self.teamsList = []
		self.url = 'removedurl'
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

	#Gets all team numbers in a given match and updates firebase with the corresponding TIMD
	def addTIMDsToFirebase(self, matches):
		print('\nDoing TIMDs...')
		timdFunc = lambda t, m: self.updateFirebaseWithTIMD(utils.makeTIMDFromTeamNumberAndMatchNumber(t, m.number))
		addTIMD = lambda m: map(lambda t: timdFunc(t, m), m.redAllianceTeamNumbers + m.blueAllianceTeamNumbers)
		map(addTIMD, matches)

	#Adds all of the slack profiles to the firebase
	def addSlackProfilesToFirebase(self):
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

	#Gets the python object for a specific location on firebase
	def getPythonObjectForFirebaseDataAtLocation(self, location):
		return utils.makeASCIIFromJSON(self.firebase.child(location).get().val())

	#Stores inputted file (data export) on firebase
	def sendExport(self, fileName):
		now = str(datetime.datetime.now())
		filePath = './' + fileName
		self.fbStorage.child('Exports').child(fileName).put(filePath)

	#Resets basic keys on firebase
	def addSingleKeysToFirebase(self):
		self.firebase.child('currentMatchNum').set(1)
		self.firebase.child('cycleCounter').set(0)
