# Restores any data deleted by schemaEnforcer stored in a backup file in 'restores' directory

import pyrebase
from Tkinter import Tk
from tkFileDialog import askopenfilename
import json

url = 'removedurl'

config = {
	"apiKey": "apikey",
    "authDomain": url + ".firebaseapp.com",
    "databaseURL": "https://" + url + ".firebaseio.com",
    "projectId": url,
    "storageBucket": url + ".appspot.com",
    "messagingSenderId": "333426669167"

}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# File selector GUI
Tk().withdraw() 
filename = askopenfilename()

with open(filename, 'r') as f:
	data = json.load(f)

for x in data:
	if x == 'key':
		for y in data[x]:
			db.child(y).set(data[x][y])