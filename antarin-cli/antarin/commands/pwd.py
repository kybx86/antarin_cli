from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json

class CurrentWorkingDirectory(Base):

	def send_request(self,token,id_val):
		try:
			#url = "http://127.0.0.1:8000/rest-pwd/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-pwd/"
			connection = requests.post(url, data = {'token':token,'id':id_val})
		except requests.ConnectionError, e:
			connection = e
		return connection

	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		token = config.get('user_details','token')
		id_val = config.get('user_details', 'id')
		if token != "":
			connection = CurrentWorkingDirectory.send_request(self,token,id_val)
			if connection.status_code == 200:
				print json.loads(json.loads(connection.text))
			else:
				print "Error connecting to server"
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."

