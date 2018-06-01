from CSVExporter import *
from scoutRotator import *
import DataModel
import firebaseCommunicator
import traceback
import Math

PBC = firebaseCommunicator.PyrebaseCommunicator()
fb = PBC.firebase
comp = DataModel.Competition(PBC)
calc = Math.Calculator(comp)

while(True):
	comp.updateTeamsAndMatchesFromFirebase()
	comp.updateTIMDsFromFirebase()
	cmd = raw_input('>>> ').split()
	if cmd[0] == 'exp':
		try:
			if cmd[1] == 'timd':
				if cmd[2] == '-all':
					CSVExportTIMDALL(comp)
					comp.PBC.sendExport('EXPORT-TIMDALL.csv')
			elif cmd[1] == 'team':
				if cmd[2] == '-all':
					CSVExportTeamALL(comp)
					comp.PBC.sendExport('EXPORT-TEAMALL.csv')
				elif cmd[2] == '-rs':
					CSVExportTeamRScores(comp)
					comp.PBC.sendExport('EXPORT-RSCORES.csv')
				elif cmd[2] == '-R':
					CSVExportTeamRichard(comp, cmd[3])
					comp.PBC.sendExport('EXPORT-' + cmd[3] + '.csv')
			elif cmd[1] == 'match':
				if cmd[2] == '-predictions':
					CSVExportMatchPredictedErrors(comp)
					comp.PBC.sendExport('EXPORT-PREDICTEDERRORS.csv')
				elif cmd[2] == '-fouls':
					CSVExportMatchFoulComparison(comp)
					comp.PBC.sendExport('EXPORT-FOULCOMPARISON.csv')
		except Exception as e:
			if len(cmd) < 3:
				print('The command exp requires 3 arguments, you provided ' + str(len(cmd)))			
			else:
				print(traceback.format_exc())
	elif cmd[0] == 'cycle':
		cycle = fb.child('cycleCounter').get().val()
		fb.child('cycleCounter').set(cycle + 1)
	elif cmd[0] == 'match':
		if len(cmd) > 1:
			try:
				int(cmd[1])
				fb.child('currentMatchNum').set(int(cmd[1]))
			except:
				print('Please input an int for an argument')
		else:
			print('The command match requires 2 arguments, you provided ' + str(len(cmd)))
	elif cmd[0] == 'test':
		print('Test completed.')
	elif cmd[0] == 'help':
		print(' exp [timd/team/match] [all] - Tries to export')
		print(' cycle - Updates cycleCounter on firebase.')
		print(' match [int] - Updates currentMatchNum on firebase.')
		print(' test - Prints Test Completed.')
	else:
		print('\'' + str(cmd[0]) + '\' is not a valid function. Type help for help.')
