from slackclient import SlackClient

with open('SlackToken.csv', 'r') as file:
	slackToken = file.read()
	
sc = SlackClient(slackToken)
userIDs = [
	'U32M6EFLP', #Ethan
	'U749CSZ36', #Carl
	'U2UPYFFGA', #Kenny
]

#Sends slack message to listed user(s)
def reportServerCrash(message):
	map(lambda u:
	sc.api_call(
		'chat.postMessage',
		channel = u,
		text = message
	), userIDs)

#Sends slack message to listed user(s)
def reportOverestimate(message):
	map(lambda u:
	sc.api_call(
		'chat.postMessage',
		channel = '@' + u,
		text = message
	), userIDs)
