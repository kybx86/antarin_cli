from .base import Base
from ConfigParser import SafeConfigParser
import json,os
import requests

class Delete(Base):
	def send_request(self,token):
		filename = json.loads(json.dumps(self.options))['<file>']
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-filedelete/" + filename			
		files = {
			'token' : (None, json.dumps(token), 'application/json'),
         	'file': (None,json.dumps(filename),'application/json')
		}
		#print files
		try:
			connection = requests.post(url, files=files)
		except e:
			connection = e
		return connection

	def run(self):
		config = SafeConfigParser()
		config.read('config.ini')
		token = config.get('user_details', 'token')
		if token != "":
			connection = Delete.send_request(self,token)
			if connection.status_code == 204:
				print "Deleted file"
			else:
				print 'Error while fetching files'
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authentication is compelete."