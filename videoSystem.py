#Last Updated: 2/11/18
import shutil
import sys
import os
import TBACommunicator
import pdb
import traceback

#Gets a list of matches to make a list of names
def getSchedule():
	tbac = TBACommunicator.TBACommunicator()
	return filter(lambda v: v['comp_level'] == 'qm', tbac.makeEventMatchesRequest())

#Creates a name for a video based on recording order, with the match number and team numbers
def getVideoKey(number):
	match = filter(lambda m: m['match_number'] == number + 1, matches)[0]
	print(matches[number]['match_number'])
	key = list('Q' + str(match['match_number']) + '_')
	teams = match['alliances']['red']['teams'] + match['alliances']['blue']['teams']
	[key.append(str(number) + '_') for number in teams]
	return ''.join(key)

#Moves all videos from the start folder to destination folder
def moveVids(folder, dest):
	#Cannot move without a start folder and a destination folder
	if not folder or not dest:
		print('Error: Folders not set')
		return
	files = os.listdir(folder)
	destFiles = os.listdir(dest)[1:]
	#Sort files by creation time
	files = sorted(files, key = lambda k: os.stat(folder + k).st_ctime)
	#Start from the first match not in destination and move each subsequent file
	if destFiles:
		matchToStartFrom = len(destFiles)
		files = files[matchToStartFrom:]
		matchesToFiles = zip(range(matchToStartFrom, len(files) + matchToStartFrom), files)
		[moveVid(getVideoKey(k), folder + fileName, dest) for k, fileName in matchesToFiles]
		return
	#Otherwise, move all files, starting from match 1
	map(lambda n: moveVid(getVideoKey(n), folder + files[n], dest), range(len(files)))

#Skips specific videos from downloading
def skip(folder, dest, number):
	files = os.listdir(folder)
	destFiles = os.listdir(dest)[1:]
	files = sorted(files, key = lambda k: os.stat(folder + k).st_ctime)
	print(len(files[:number - 1]))
	for f in files[:number - 1]:
		moveVid(getVideoKey(files.index(f)), folder + f, dest)
	print(files[number - 1:])
	for f in files[number - 1:]:
		moveVid(getVideoKey(files.index(f) + 1), folder + f, dest)

#Deletes the most recent match for a replay
def replayLastMatch(folder):
	#Start folder and recorded match needed for replay
	if not folder:
		print('ERROR: Folders not set')
		return
	if not len(os.listdir(folder)):
		print('ERROR: No match to replay')
		return
	files = os.listdir(folder)
	#Delete the most recent video, to make room for the replay
	files = sorted(files, key = lambda k: os.stat(folder + k).st_ctime)
	fileToDelete = files[-1]
	print(folder + fileToDelete)
	os.remove(folder + fileToDelete)

#Moves a video from the original location to a new location with a new name
def moveVid(key, filePath, dest):
	print(key)
	print(filePath)
	shutil.copy(filePath, dest + key + '.mov')

print('Downloading schedule...')
matches = getSchedule()
#If two folder locations were entered when starting, the first is the folder the videos start in and the second is the folder they move to
try:
	videoFolder = sys.argv[1]
	destFolder = sys.argv[2]
#Otherwise, the folder locations need to be entered later
except KeyboardInterrupt:
	return
except:
	videoFolder = ''
	destFolder = ''

print("Video system 2017. Type 'help' for a list of commands.")

#Loop looks for input and runs commands
while(True):
	cmd = raw_input('>>> ').split()
	if not cmd: continue
	try:
		if cmd[0] == 'setdest':
			destFolder = cmd[1]
	except KeyboardInterrupt:
		return
	except:
		print('Error: Must supply more arguments')
	try:
		if cmd[0] == 'setvid':
			videoFolder = cmd[1]
	except KeyboardInterrupt:
		return
	except:
		print('Error: Must supply more arguments')
	if cmd[0] == 'replay':
		replayLastMatch(videoFolder)
	elif cmd[0] == 'done':
		moveVids(videoFolder, destFolder)
	elif cmd[0] == 'skip':
		try:
			skip(videoFolder, destFolder, int(cmd[1]))
		except KeyboardInterrupt:
			return
		except:
			print(traceback.format_exc())
	elif cmd[0] == 'help':
		print('setdest [FILEPATH] - Reset the file path to which you want videos to be moved')
		print('setvid [FILEPATH] - Reset the file path to which unnamed videos will be stored')
		print('replay - Delete last recording (RUN THIS BEFORE RECORDING ANYTHING ELSE)')
		print('done - Run the video mover and organize all video files by match (run at the end of the day)')
		print('skip - Skip specific videos and folders from download')
