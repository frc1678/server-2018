#Last Updated: 1/13/18
from CSVExporter import *
from scoutRotator import *
from SPR import ScoutPrecision
import DataModel
import firebaseCommunicator
import traceback
import numpy as np
import Math
from pydub import AudioSegment
from pydub.playback import play

PBC = firebaseCommunicator.PyrebaseCommunicator()
fb = PBC.firebase
comp = DataModel.Competition(PBC)
calc = Math.Calculator(comp)
spr = ScoutPrecision()

while(True):
	comp.updateTeamsAndMatchesFromFirebase()
	comp.updateTIMDsFromFirebase()
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
	elif cmd[0] == 'calc':
		if cmd[1] == 'full':
			calc.doCalculations(PBC)
			PBC.updateFire
	elif cmd[0] == 'sns':
		tempTIMDs = fb.child('TempTeamInMatchDatas').get().val()
		curMatch = fb.child('currentMatchNum').get().val() 
		availability = fb.child('availability').get().val()
		unavailable = filter(lambda x: availability[x] == 0, availability.keys())
		sentScouts = []
		print(unavailable)
		for TIMD, value in tempTIMDs.items():
			if value['matchNumber'] == curMatch:
				sentScouts.append(value['scoutName'])
		notSentScouts = np.setdiff1d(scouts, sentScouts)
		notSentScoutNums = []
		for scout in notSentScouts:
			notSentScoutNums.append(str(spr.getScoutNumFromName(scout, fb.child('scouts').get().val())))
		print('Scouts that have not sent - ' + ", ".join(notSentScoutNums))
	elif cmd[0] == 'play':
		try:
			play(AudioSegment.from_mp3('/home/etking/Music/' + cmd[1] + '.mp3'))
		except:
			print('\'' + str(cmd[1]) + '\' is not a sound on the soundboard.')
	elif cmd[0] == 'test':
		print('Test completed.')
	elif cmd[0] == 'help':
		print('exp [timd/team] [all] - Tries to export')
		print('sns - Prints the scouts that haven\'t sent for current match')
		print('test - Prints Test Completed.')
	else:
		print('\'' + str(cmd[0]) + '\' is not a valid function. Type help for help.')
