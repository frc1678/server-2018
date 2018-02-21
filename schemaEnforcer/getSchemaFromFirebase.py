import pyrebase
import json

#url = 'servervartest-2018'
#url = 'scouting-2018-9023a'
#url = 'scouting-2018-temp'
url = 'schema-enforcer'

config = {
	"apiKey": "AIzaSyBXfDygtDWxzyRaLFO75XeGc2xhfvLLwkU ",
    "authDomain": url + ".firebaseapp.com",
    "databaseURL": "https://" + url + ".firebaseio.com",
    "projectId": url,
    "storageBucket": url + ".appspot.com",
    "messagingSenderId": "333426669167"

}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

data = db.child("").get().val()


with open('./importedData.json', 'w') as f:
	json.dump(data, f, indent=4, separators=(',', ':'))

print("Done.")