import DataModel
import firebaseCommunicator
import TBACommunicator
import utils

#This file is meant to be run before each competition
#to add teams and the match schedule to the firebase

TBAC = TBACommunicator.TBACommunicator()
PBC = firebaseCommunicator.PyrebaseCommunicator()

#Prints out the firebase url so that the wrong firebase doesn't get wiped
print(PBC.url)

competition = DataModel.Competition(PBC)
competition.eventCode = TBAC.code
competition.PBC.JSONteams = TBAC.makeEventTeamsRequest()
competition.PBC.JSONmatches = TBAC.makeEventMatchesRequest()
competition.PBC.wipeDatabase()
competition.PBC.addSlackProfilesToFirebase()
competition.PBC.addSingleKeysToFirebase()
competition.PBC.addTeamsToFirebase()
competition.updateTeamsAndMatchesFromFirebase()
#You need to create the matches and teams before you call this
competition.PBC.addTIMDsToFirebase(competition.matches)
