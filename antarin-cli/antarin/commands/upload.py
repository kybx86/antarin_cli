
from .base import Base
from ConfigParser import SafeConfigParser
import json, urllib2, urllib,os
import requests

class Upload(Base):
	def send_request(self,token):
		filename = json.loads(json.dumps(self.options))['<file>']
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-fileupload/" + filename			
		files = {
			'token' : (None, json.dumps(token), 'application/json'),
         	'file': (os.path.basename(filename), open(filename, 'rb'), 'application/octet-stream')
		}
		#print files
		try:
			connection = requests.put(url, files=files)
		except e:
			connection = e
		return connection

	def run(self):
		config = SafeConfigParser()
		config.read('config.ini')
		token = config.get('user_details', 'token')
		if token != "":
			connection = Upload.send_request(self,token)
			#print "File upload successful"
			#print connection.status_code
			if connection.status_code == 204:
				print "File upload successful"
			else:
				print 'Error while fetching files'
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."


