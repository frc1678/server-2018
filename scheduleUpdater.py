#Last Updated: 1/14/18
import firebaseCommunicator
import TBACommunicator

PBC = firebaseCommunicator.PyrebaseCommunicator()
fb = PBC.firebase
tbac = TBACommunicator.TBACommunicator()

lastUpdated = None

# Checks current match, updates currentMatchNum 1 (ONE) time when called
def update():
	global lastUpdated
	currentMatchNum = fb.child('currentMatchNum').get().val()
	if lastUpdated == None:
		request = tbac.makeScheduleUpdaterRequest(currentMatchNum, {})
	else:
		request = tbac.makeScheduleUpdaterRequest(currentMatchNum, {'If-Modified-Since':lastUpdated})
	if request[0] == 200: # Ensures request succeeds
		lastUpdated = request[1]['Last-Modified']
		if request[2]['match_number'] > 0:
			fb.child('currentMatchNum').set(currentMatchNum+1)
			lastUpdated = None

