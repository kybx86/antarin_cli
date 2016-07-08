
from .base import Base
from ConfigParser import SafeConfigParser
import json, urllib2, urllib,os
import requests

class Upload(Base):
	"""docstring for Upload"""
	def send_request(self,token):
		filename = json.loads(json.dumps(self.options))['<file>']
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-fileupload/" + filename
		#val = {"token":token}
		files = {
			'token' : (None, json.dumps(token), 'application/json'),
         	'file': (os.path.basename(filename), open(filename, 'rb'), 'application/octet-stream')
		}
		try:
			connection = requests.put(url, files=files)
			#print files
		except e:
			connection = e
		return connection

	def run(self):
		config = SafeConfigParser()
		config.read('config.ini')
		token = config.get('user_details', 'token')
		if token != "":
			connection = Upload.send_request(self,token)
			print "File upload successful"
			#print connection
			# if connection.code == 204:
			# 	data = connection.read()
			# 	print data
			# else:
			# 	print 'Error while fetching files'
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."


