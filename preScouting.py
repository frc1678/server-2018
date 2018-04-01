import TBACommunicator
import firebaseCommunicator
import DataModel
import utils
import csv

TBAC = TBACommunicator.TBACommunicator()
pbc = firebaseCommunicator.PyrebaseCommunicator()
comp = DataModel.Competition(pbc)
db = pbc.firebase

teams = [team['key'] for team in TBAC.makeEventTeamsRequest()]
selected = ['team', 'autoRun', 'climb']
masterList = []

print('Begining prescouting...')

for team in teams:
	events = [event['event_code'] for event in TBAC.makeTeamEventsRequest(team) if event['week'] < 4]
	autoRuns = []
	climbs = []
	print('Prescouting for ' + team.split('c')[1] + '...')
	for event in events:
		matches = TBAC.makeRequest(TBAC.basicURL + 'team/' + team + '/event/' + str(TBAC.year) + event + '/matches')
		for match in matches:
			allianceColor = 'blue' if team in match['alliances']['blue']['team_keys'] else 'red'
			robotNum = (match['alliances'][allianceColor]['team_keys'].index(team)) + 1
			autoRuns += [True if match['score_breakdown'][allianceColor]['autoRobot' + str(robotNum)]  == 'AutoRun' else False]
			climbs += [True if match['score_breakdown'][allianceColor]['endgameRobot' + str(robotNum)]  == 'Climbing' else False]
	if events:
		masterList += [{'team' : team, 'autoRun' : utils.avg(autoRuns), 'climb' : utils.avg(climbs)}]
	else:
		masterList += [{'team' : team, 'autoRun' : None, 'climb' : None}]

print('Prescouting Complete. Exporting to csv...')

with open('./prescout.csv', 'w') as f:
	writer = csv.DictWriter(f, fieldnames = selected)
	writer.writeheader()
	for team in masterList:
		writer.writerow({k : team[k] for k in selected})

print('Export complete.')
