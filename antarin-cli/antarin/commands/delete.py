from .base import Base
from ConfigParser import SafeConfigParser
import json,os
import requests
from os.path import expanduser

class Delete(Base):
	def send_request(self,token):
		filename = json.loads(json.dumps(self.options))['<file>']
		url = "http://127.0.0.1:8000/rest-filedelete/"			
		files = {
			'token' : (None, json.dumps(token), 'application/json'),
         	'file': (None,json.dumps(filename),'application/json')
		}
		try:
			connection = requests.post(url, files=files)
		except e:
			connection = e
		return connection

	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.config.ini'
		config.read(filepath)
		token = config.get('user_details', 'token')
		if token != "":
			connection = Delete.send_request(self,token)
			if connection.status_code == 204:
				print "Deleted file : %s" %json.loads(json.dumps(self.options))['<file>']
			#write specific error messages for all potential connection failure status codes
			else:
				print 'Error while fetching files'
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authentication is compelete."