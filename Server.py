#By Bryton Moeller (2015-2016)
#Last Updated: 2/1/18
import sys
import traceback
import DataModel
import firebaseCommunicator
import Math
import time
import CSVExporter
import pdb
from CrashReporter import reportServerCrash
import dataChecker
from scoutRotator import ScoutRotator
import scheduleUpdater
import pprint

PBC = firebaseCommunicator.PyrebaseCommunicator()
comp = DataModel.Competition(PBC)
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()
calculator = Math.Calculator(comp)
cycle = 1
scheduleUpdater.scheduleListener()
shouldSlack = True
consolidator = dataChecker.DataChecker()
consolidator.start()
fb = PBC.firebase
fb.child('availabilityUpdated').set(0)

#Scout assignment streams:

#Note: availability child on firebase should have each scout with an availability of 1 or 0
	#If that isn't the case, use ScoutRotator.tabletHandoutStream() for resetAvailability()

#Assign Scouts and Tablet Handouts- reset ALL scouts at beggining of day in a comp
#If the server crashes and you don't wanna reset scouts already on fb, then input 'no'
ScoutRotator.notSimpleStream()

#Use this if you are restarting the server and need to reassign scouts but scouts already have tablets
#Also useful for unexpected changes in availability
#Note: Only use if availability child on Firebase has each scout with a value of 1 or 0

# ScoutRotator.simpleStream()

def checkForMissingData():
	with open('missing_data.txt', 'w') as missingDataFile:
		missingDatas = calculator.getMissingDataString()
		if missingDatas:
			print(missingDatas)
		missingDataFile.write(str(missingDatas))

while(True):
	print("\033[0;37m")
	print('\033[1;32mCalcs Cycle ' + str(cycle) + '...')
	print("\033[0;37m")
	if cycle % 5 == 1:
		PBC.cacheFirebase()
	while(True):
		#updates all matches in firebase
		try:
			comp.updateTeamsAndMatchesFromFirebase()
			comp.updateTIMDsFromFirebase()
			break
		except Exception as e:
			print(e)
	checkForMissingData() #opens missing_data.txt and prints all missing data if there is missing data each cycle
	try:
		calculator.doCalculations(PBC)
	except OSError:
		continue
	except:
		#reports error to slack
		if shouldSlack:
			reportServerCrash(traceback.format_exc())
		#prints the error if shouldSlack isn't True
		else:
			print(traceback.format_exc())
		sys.exit(0)
	time.sleep(1)
	cycle += 1
