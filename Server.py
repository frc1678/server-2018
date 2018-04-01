#By Bryton Moeller (2015-2016)
#Last Updated: 3/15/18
import sys
import traceback
import DataModel
import firebaseCommunicator
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

#If an argument is passed when running the server, it skips confirmation
forced = False
if len(sys.argv) > 1:
	if sys.argv[1] == '-f':
		forced = True

#Updates variables data to the local DataModel
TBAC = TBACommunicator.TBACommunicator()
PBC = firebaseCommunicator.PyrebaseCommunicator()
comp = DataModel.Competition(PBC)
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()
calculator = Math.Calculator(comp)
cycle = 1
fb = PBC.firebase
shouldSlack = False

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
		if confirmation == 'y':
			break
		elif confirmation == 'n':
			sys.exit()
		else:
			print(' ' + confirmation + ' is not a valid option. \n')

#Imports dataChecker and runs it later to avoid a subprocess being created before confirmation
import dataChecker

consolidator = dataChecker.DataChecker()
consolidator.start()

#Scout assignment streams:

#Note: availability child on firebase should have each scout with an availability of 1 or 0
	#If that isn't the case, use ScoutRotator.tabletHandoutStream() for resetAvailability()

#Use this if tablets need assigned to scouts by the server, and will then be given to the correct scouts
#This means at the beginning of a competition day
scoutRotator.tabletHandoutStream()

#Use this for running the server again (e.g. after a crash) to avoid reassigning scouts or tablets
#scoutRotator.alreadyAssignedStream()

#Use this if you are restarting the server and need to reassign scouts but scouts already have tablets
#Also useful for unexpected changes in availability
#Note: Only use if availability child on Firebase has each scout with a value of 1 or 0

#scoutRotator.simpleStream()

def checkForMissingData():
	with open('missing_data.txt', 'w') as missingDataFile:
		missingDatas = calculator.getMissingDataString()
		missingDataFile.write(str(missingDatas))

while(True):
	print('\033[0;37m')
	print('\033[1;32mCalcs Cycle ' + str(cycle) + '...')
	print('\033[0;37m')
	if cycle % 5 == 1:
		PBC.cacheFirebase()
	while(True):
		#updates all matches in firebase
		try:
			comp.updateTeamsAndMatchesFromFirebase()
			comp.updateTIMDsFromFirebase()
			break
		except KeyboardInterrupt:
			break
		except Exception as e:
			print(e)
			print(traceback.format_exc())
	checkForMissingData() #opens missing_data.txt and prints all missing data if there is missing data each cycle
	try:
		calculator.doCalculations(PBC)
	except OSError:
		continue
	except KeyboardInterrupt:
		sys.exit()
		consolidator.terminate()
		consolidator.join()
	except:
		#reports error to slack
		if shouldSlack:
			reportServerCrash(traceback.format_exc())
		print(traceback.format_exc())
		sys.exit(0)
	time.sleep(1)
	cycle += 1
