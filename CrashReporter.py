#Last Updated: 2/11/18
from slackclient import SlackClient

with open('SlackToken.csv', 'r') as SlackToken:
	slackToken = SlackToken.read()
sc = SlackClient(slackToken)

et = 'U32M6EFLP'
cc = 'U749CSZ36'
kz = 'U2UPYFFGA'
#Sends slack message to listed user(s)
def reportServerCrash(message):
	map(lambda u:
	sc.api_call(
		'chat.postMessage',
		channel = u,
		text = message
	), [et, cc, kz])

#Sends slack message to listed user(s)
def reportOverestimate(message):
	map(lambda u:
	sc.api_call(
		'chat.postMessage',
		channel = '@' + u,
		text = message
	), [et, cc, kz])
