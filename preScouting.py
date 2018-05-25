import TBACommunicator
import firebaseCommunicator
import DataModel
import utils
import csv

#The purpose of this file is to create a csv file filled with data about 
#all of the teams in a competition from all of their previous competitions, 
#including autoRun, climb, autoScale, and autoSwitch datapoints

TBAC = TBACommunicator.TBACommunicator()
pbc = firebaseCommunicator.PyrebaseCommunicator()
comp = DataModel.Competition(pbc)
db = pbc.firebase

teams = [team['key'] for team in TBAC.makeEventTeamsRequest()]
selected = ['team', 'autoRun', 'climb', 'autoScale', 'autoSwitch']
masterList = []

print('Begining prescouting...')
auto = {}
for team in teams:
	full = {event['event_code'] : event['week'] for event in TBAC.makeTeamEventsRequest(team)}
	events = sorted([event for event in full.keys()], key = lambda event: full[event])
	event = events[-1]
	autoRuns = []
	climbs = []
	autoScales = []
	autoSwitches = []
	print('Prescouting for ' + team.split('c')[1] + '...')
	for event in events:
		matches = TBAC.makeRequest(TBAC.basicURL + 'team/' + team + '/event/' + str(TBAC.year) + event + '/matches')
		for match in matches:
			allianceColor = 'blue' if team in match['alliances']['blue']['team_keys'] else 'red'
			robotNum = (match['alliances'][allianceColor]['team_keys'].index(team)) + 1
			autoRuns += [True if match['score_breakdown'][allianceColor]['autoRobot' + str(robotNum)]  == 'AutoRun' else False]
			climbs += [True if match['score_breakdown'][allianceColor]['endgameRobot' + str(robotNum)]  == 'Climbing' else False]
			autoScales += [match['score_breakdown'][allianceColor]['autoScaleOwnershipSec']]
			autoSwitches += [match['score_breakdown'][allianceColor]['autoSwitchOwnershipSec']]
	if events:
		masterList += [{'team' : team, 'autoRun' : utils.avg(autoRuns), 'climb' : utils.avg(climbs), 'autoScale' : utils.avg(autoScales), 'autoSwitch' : utils.avg(autoSwitches)}]
	else:
		masterList += [{'team' : team, 'autoRun' : None, 'climb' : None, 'autoSwitch' : None, 'autoScale' : None}]

print('Prescouting Complete. Exporting to csv...')

with open('./prescout.csv', 'w') as f:
	writer = csv.DictWriter(f, fieldnames = selected)
	writer.writeheader()
	for team in masterList:
		writer.writerow({k : team[k] for k in selected})

print('Export complete.')
