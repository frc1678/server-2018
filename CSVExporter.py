#CSV Exporter, by Bryton 2/10/16
import csv
from DataModel import *
import Math

#Puts scout z-scores in csv file
def CSVExportScoutZScores(zscores):
	with open('./scoutRankExport.csv', 'w') as f:
		writer = csv.DictWriter(f, fieldnames = ['name', 'spr', 'Z-Score', 'matches'])
		writer.writeheader()
		for k, v in zscores.items():
			writer.writerow({'name' : k, 'spr' : zscores[k][1], 'Z-Score' : zscores[k][0], 'matches' : zscores[k][2]})

#Puts some scouted and calculated data in csv file
def CSVExportTeam(comp, name, keys = []):
	calculator = Math.Calculator(comp)
	excluded = ['calculatedData', 'name', 'imageKeys', 'pitAllImageURLs', 'pitSelectedImageName']
	with open('./EXPORT-' + name + '.csv', 'w') as f:
		defaultKeys = [k for k in Team().__dict__.keys() if k not in excluded and k in keys]
		defaultKeys += [k for k in Team().calculatedData.__dict__.keys() if k in keys]
		defaultKeys = sorted(defaultKeys, key = lambda k: (k != 'number', k.lower()))
		writer = csv.DictWriter(f, fieldnames = defaultKeys)
		writer.writeheader()
		for team in comp.teams:
			team.numMatchesPlayed = len(calculator.su.getCompletedMatchesForTeam(team))
			tDict = team.__dict__
			tDict.update(team.calculatedData.__dict__)
			keys = sorted(defaultKeys, key = lambda k: (k != 'number', k.lower()))
			writer.writerow({k : tDict[k] for k in keys})

#Puts some scouted and calculated data in csv file
def CSVExportTIMD(comp, name, keys = []):
	calculator = Math.Calculator(comp)
	excluded = ['calculatedData']
	with open('./EXPORT-' + name + '.csv', 'w') as f:
		defaultKeys = [k for k in TeamInMatchData().__dict__.keys() if k not in excluded and k in keys]
		defaultKeys += [k for k in TeamInMatchData().calculatedData.__dict__.keys() if k in keys]
		defaultKeys = sorted(defaultKeys, key = lambda k: (k != 'matchNumber' and k != 'teamNumber', k.lower()))
		writer = csv.DictWriter(f, fieldnames = defaultKeys)
		writer.writeheader()
		comp.updateTIMDsFromFirebase()
		for timd in comp.TIMDs:
			tDict = timd.__dict__
			tDict.update(timd.calculatedData.__dict__)
			keys = sorted(defaultKeys, key = lambda k: (k != 'matchNumber' and k != 'teamNumber', k.lower()))
			writer.writerow({k : tDict[k] for k in keys})

def CSVExportMatch(comp, name, keys = []):
	calculator = Math.Calculator(comp)
	excluded = ['calculatedData', 'name']
	with open('./EXPORT-' + name + '.csv', 'w') as f:
		defaultKeys = [k for k in Match().__dict__.keys() if k not in excluded and k in keys]
		defaultKeys += [k for k in Match().calculatedData.__dict__.keys() if k in keys]
		defaultKeys = sorted(defaultKeys, key = lambda k: (k != 'number', k.lower()))
		writer = csv.DictWriter(f, fieldnames = defaultKeys)
		writer.writeheader()
		for match in comp.matches:
			tDict = match.__dict__
			tDict.update(match.calculatedData.__dict__)
			keys = sorted(defaultKeys, key = lambda k: (k != 'number', k.lower()))
			writer.writerow({k : tDict[k] for k in keys})
