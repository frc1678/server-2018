import pyrebase

class SettingsCommunicator(object):
	'''docstring for SettingsCommunicator'''
	def __init__(self):
		super(SettingsCommunicator, self).__init__()
		self.url = 'url'
		config = {
			'apiKey': 'mykey',
			'authDomain': self.url + '.firebaseapp.com',
			'storageBucket': self.url + 'appspot.com',
			'databaseURL': 'https://' + self.url + '.firebaseio.com/'
		}
		app = pyrebase.initialize_app(config)
		self.firebase = app.database()