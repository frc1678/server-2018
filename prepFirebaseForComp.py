#Last Updated: 8/26/17
import DataModel
import firebaseCommunicator
import TBACommunicator
import utils

############# Getting TBA Data ###################
#Set to '<your initials>:TBA_communicator:0'

TBAC = TBACommunicator.TBACommunicator()
PBC = firebaseCommunicator.PyrebaseCommunicator()
print(PBC.url)
competition = DataModel.Competition(PBC)
competition.eventCode = TBAC.code
competition.PBC.JSONteams = TBAC.makeEventTeamsRequest()
competition.PBC.JSONmatches = TBAC.makeEventMatchesRequest()
#competition.PBC.wipeDatabase()
#competition.PBC.addSlackProfilesToFirebase()
#competition.PBC.addSingleKeysToFirebase()
#competition.PBC.addTeamsToFirebase()
competition.PBC.addSketchyMatchesToFirebase()
competition.updateTeamsAndMatchesFromFirebase()
competition.PBC.addTIMDsToFirebase(competition.matches) #You need to create the matches and teams before you call this
