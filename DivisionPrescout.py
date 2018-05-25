import TBACommunicator
import os
import random

TBAC = TBACommunicator.TBACommunicator()
key = [[], [5], [5, 5], [4, 3, 3], [2, 2, 3, 3], [2, 2, 2, 2, 2], [1, 1, 2, 2, 2, 2], [1, 1, 1, 1, 2, 2, 2], [1, 1, 1, 1, 1, 1, 2, 2]]
teams = []
teams = ['frc' + team for team in teams]
path = 'path/to/outputFile/'

for team in teams:
	events = [event['event_code'] for event in TBAC.makeTeamEventsRequest(team)]
	urls = {}
	print('Prescouting for ' + team.split('c')[1] + '...')
	eventDict = {event : key[len(events)][index] for index, event in enumerate(events)}
	for event in events:
		eve = TBAC.makeRequest(TBAC.basicURL + 'event/' + str(TBAC.year) + event)
		name = str(eve['week']) + '-' + eve['name']
		urls[name] = {}
		matches = TBAC.makeRequest(TBAC.basicURL + 'team/' + team + '/event/' + str(TBAC.year) + event + '/matches')
		matches = [match for match in matches if match['videos'] != []]
		finals = filter(lambda m: m['comp_level'] == 'f' or m['comp_level'] == 'sf' or m['comp_level'] == 'qf', matches)
		quals = filter(lambda m: m['comp_level'] == 'qm', matches)
		numMatches = eventDict[event]
		weight = 1.0
		if finals != []:
			for x in range((int(round(numMatches * 0.5)) + 1)):
				if finals == []:
					break
				match = random.choice(finals)
				del finals[finals.index(match)]
				video = [vid['key'] for vid in match['videos']]
				if video != []:
					video = video[0]
					urls[name][(match['comp_level'] + str(match['match_number']))] = video
				else:
					break
			else:
				weight = 0.5
		for x in range((int(round(numMatches * weight)))):
			try:
				match = random.choice(quals)
				del quals[quals.index(match)]
				video = [vid['key'] for vid in match['videos']]
				if video:
					video = video[0]
					urls[name][(match['comp_level'] + str(match['match_number']))] = video
			except:
				pass
	
	for event, videos in urls.items():
		for number, url in videos.items():
			os.system('youtube-dl -k -o \'' + path + str(team) + '/' + str(event) + '/' + str(number) + '.mp4\' \'https://www.youtube.com/watch?v=' + str(url) + '\'  -f \'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[height<=720]\'')
