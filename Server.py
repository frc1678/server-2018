#By Bryton Moeller (2015-2016)
import sys
import traceback
import DataModel
import firebaseCommunicator
import settingsCommunicator
import Math
import time
import CSVExporter
import pdb
from CrashReporter import reportServerCrash
import scoutRotator
import scheduleUpdater
import pprint
import APNServer
import TBACommunicator
import dataChecker

#If an 'f' argument is passed when running the server, it skips confirmation
forced = False
if len(sys.argv) > 1:
	if sys.argv[1] == '-f':
		forced = True

#Updates variables data to the local DataModel
TBAC = TBACommunicator.TBACommunicator()
PBC = firebaseCommunicator.PyrebaseCommunicator()
SC = settingsCommunicator.SettingsCommunicator()
comp = DataModel.Competition(PBC)
calculator = Math.Calculator(comp)
cycle = 1
fb = PBC.firebase
shouldSlack = False
calculator.addTBAcode(PBC)
SC.firebase.child('calcCycleUpdate').set(0)
SC.firebase.child('isFull').set(0)

#Scout assignment streams:

#Note: availability child on firebase should have each scout with an availability of 1 or 0
#If that isn't the case, use ScoutRotator.tabletHandoutStream() for resetAvailability()

#Use this if tablets need assigned to scouts by the server, and will then be given to the correct scouts
#This means at the beginning of a competition day
if len(sys.argv) > 1:
	if sys.argv[1] == '-t':
		scoutRotator.resetAvailability()

#Use this if you are restarting the server and need to reassign scouts but scouts already have tablets
#Also useful for unexpected changes in availability
#Note: Only use if availability child on Firebase has each scout with a value of 1 or 0

#scoutRotator.simpleStream()

#If forced is not true, it runs confirmation to prevent running the server on the wrong competition, firebase, etc.
if forced != True:
	print('\n    _______________SERVER_______________')
	print('                                        ')
	print('    Firebase - ' + PBC.url)
	print('    Firebase Competition - ' + fb.child('TBAcode').get().val())
	print('    TBACommunicator Competition - ' + TBAC.code + ' (Should be the same as above)')
	print('    Available Scouts - ' + str(len([scout for scout, available in fb.child('availability').get().val().items() if available == 1])))
	print('                                          ')
	while True:
		confirmation = raw_input(' Do you wish to continue? [y/n] ')
		# '.lower()' used to allow for capital Y/N
		if confirmation.lower() == 'y':
			break
		elif confirmation.lower() == 'n':
			sys.exit()
		else:
			print(' ' + confirmation + ' is not a valid option. \n')

consolidator = dataChecker.DataChecker()

def checkForMissingData():
	with open('missing_data.txt', 'w') as missingDataFile:
		missingDatas = calculator.getMissingDataString()
		missingDataFile.write(str(missingDatas))

def calcCycle(data):
	if data['data'] == 0:
		return
	comp.updateCurrentMatchFromFirebase()
	cycle = comp.currentMatchNum
	isFull = bool(SC.firebase.child('isFull').get().val())
	print('\033[0;37m')
	print('\033[1;32mCalcs Cycle For Match ' + str(cycle) + '...')
	print('\033[0;37m')
	while(True):
		#Updates all matches in firebase
		try:
			print('> Doing SPRs!')
			scoutRotator.doSPRs()
			print('> Consolidating tempTIMDs')
			consolidator.run(isFull)
			comp.updateTeamsAndMatchesFromFirebase()
			comp.updateTIMDsFromFirebase()
			break
		except KeyboardInterrupt:
			break
		except Exception as e:
			print(e)
			print(traceback.format_exc())
	checkForMissingData() #Opens missing_data.txt and prints all missing data if there is missing data each cycle
	try:
		calculator.doCalculations(PBC, isFull)
	except OSError:
		pass
	except KeyboardInterrupt:
		sys.exit()
	except:
		#Reports error to slack
		if shouldSlack:
			reportServerCrash(traceback.format_exc())
		print(traceback.format_exc())
		sys.exit(0)
	SC.firebase.child('calcCycleUpdate').set(0)
	SC.firebase.child('isFull').set(0)
	print('> Calc cycle ' + str(cycle) + ' finished up!')

print('Setup is finished! Ready to start cycles!')
SC.firebase.child('calcCycleUpdate').stream(calcCycle)
