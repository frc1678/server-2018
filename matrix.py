#Last Updated: 8/26/17
import TBACommunicator
import numpy as np
from schemaUtils import SchemaUtils
import DataModel 
import firebaseCommunicator as f
import Math

#Taking data from TBA, setting up the schemaUtils class, and defining variables to use later on
comp = DataModel.Competition(f.PyrebaseCommunicator())
calculator = Math.Calculator(comp)
su = SchemaUtils(comp, calculator) #Add actual parameters before competition
TBA = TBACommunicator.TBACommunicator()
listOfMatches = TBA.makeEventMatchesRequest()
teamsToListPlacement = {}
listOfTeams = TBA.makeEventTeamsRequest()

#Creates the base array to be added to later
matrix = np.zeros((len(listOfTeams), len(listOfTeams)), dtype = np.int)
print(listOfTeams)

#Enumerates each team from the list of teams into teamsToListPlacement
for listPlacement in range(0, (len(listOfTeams) - 1)): teamsToListPlacement[listOfTeams[listPlacement]] = listPlacement

#Iterates through all of the matches and adds to the matrix
for match in listOfMatches:
	for team in su.teamsInMatch(match):
		if getTeamAllianceIsRedInMatch(team, match) == True:
			for allianceTeam in getAllianceInMatch(match, True):
				matrix[teamsToListPlacement.get(team)][teamsToListPlacement.get(allianceTeam)] += 1
		elif getTeamAllianceIsRedInMatch(team, match) == False:
			for allianceTeam in getAllianceInMatch(match, False):
				matrix[teamsToListPlacement.get(team)][teamsToListPlacement.get(allianceTeam)] += 1
