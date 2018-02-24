#Last Updated: 1/13/18
from CSVExporter import *
import DataModel
import firebaseCommunicator
import traceback

PBC = firebaseCommunicator.PyrebaseCommunicator()
fb = PBC.firebase
comp = DataModel.Competition(PBC)

while(True):
	comp.updateTeamsAndMatchesFromFirebase()
	cmd = raw_input('>>> ').split()
	if cmd[0] == 'exp':
		try:
			if cmd[1] == 'timd':
				if cmd[2] == 'all':
					CSVExportTIMDALL(comp)
					comp.PBC.sendExport('EXPORT-TIMDALL.csv')
				elif cmd[2] == 'other':
					print('')
			elif cmd[1] == 'team':
				if cmd[2] == 'all':
					CSVExportTeamALL(comp)
					comp.PBC.sendExport('EXPORT-TEAMALL.csv')
				elif cmd[2] == 'other':
					print('')
		except Exception as e:			
			print(traceback.format_exc())
	elif cmd[0] == 'sns':
		#idea for faster method- under TempTIMDs, have data organized by match, and under that, the data, so we don't have to iterate through every TIMD
		scoutSentData = []
		scoutNotSentData = []
		tempTIMDs = fb.child('TempTeamInMatchDatas').get().val()
		curMatch = str(fb.child('currentMatchNum').get().val())
		for TIMD in tempTIMDs:
			name = fb.child('TempTeamInMatchDatas').child(TIMD).get().key()
			scout = name[-2:]
			if '-' in scout:
				scout = scout[1:]
			match = name.split('-')[0]
			match = match[-2:]
			if 'Q' in match:
				match = match[-1:]
			if str(match) == curMatch:
				scoutSentData.append(scout)
		control = [str(x) for x in range(1, 19)]
		for scout in control:
			if scout not in scoutSentData:
				scoutNotSentData.append(scout)
		scoutNotSent = ''
		if scoutNotSentData != scoutNotSent:
			for scout in scoutNotSentData:
				print('Scouts that have not inputted data in match:' + str(curMatch) + '-' + scout)
		else:
			print('All scouts have sent data.')
	elif cmd[0] == 'test':
		print('Test completed.')
	elif cmd[0] == 'help':
		print('exp [timdall/teamall] - Tries to export')
		print('sns - Prints the scouts that haven\'t sent for current match')
		print('test - Prints Test Completed.')
	else:
		print('\'' + str(cmd[0]) + '\' is not a valid function. Type help for help.')
