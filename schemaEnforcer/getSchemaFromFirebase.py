# Gets the correct schema layout from a separate firebase for schemaEnforcer only

import pyrebase
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

# Gets all data from the database
data = db.child("").get().val()


with open('./importedData.json', 'w') as f:
	json.dump(data, f, indent=4, separators=(',', ':'))

print("Done.")