'''
#Last Updated: 8/26/17
from apns import APNs, Frame, Payload
import pyrebase as pyb
import pdb
import firebaseCommunicator

apns = APNs(use_sandbox = True, cert_file = './apn-cert.pem')
PBC = firebaseCommunicator.PyrebaseCommunicator()
fb = PBC.firebase

#Notifies how many matches away the inputted match is
def sendNoti(number, match, token):
        msg1 = 'Match ' + str(number) + ' is'
        msg2 = str(abs(number - match)) + ' matches away!' if (abs(number - match)) != 1 else ' up next!' if (abs(number - match)) == 0 else 'match away!' 
        red = fb.child('Matches').child(number).child('redAllianceTeamNumbers').get().val()
        blue = fb.child('Matches').child(number).child('blueAllianceTeamNumbers').get().val()
        message = msg1 + msg2
        message += '| Red: ' + ''.join(map(lambda t: str(t), red))
        message += '| Blue: ' + ''.join(map(lambda t: str(t), blue))
        payload = Payload(alert = message, sound = 'default', badge = 1)
        apns.gateway_server.send_notification(token, payload)

#Notifies user for every starred match- based on sendNoti
def sendNotiForUser(usr, currentMatchNum):
        token = usr['Token']
        starred = usr.get('StarredMatches').values() if 'StarredMatches' in usr.keys() else []
        print(starred)
        observedMs = filter(lambda n: (n - currentMatchNum) <= 2 and (n - currentMatchNum) >= 0, starred)
        print(observedMs)
        [sendNoti(n, currentMatchNum, token) for n in observedMs]

#Notifies multiple users- based on sendNotiForUser
def sendNotiForUsers(data):
        if data.get('data') == None: return
        currentMatchNum = int(data.get('data'))
        users = fb.child('AppTokens').get().val() or {}
        [sendNotiForUser(u, currentMatchNum) for u in users.values()]

#Starts the stream
def startNotiStream():
        fb.child('currentMatchNum').stream(sendNotiForUsers)

startNotiStream()
'''
