from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests

class Logout(Base):

	def send_request(self,token):
		try:
			#url = "http://127.0.0.1:8000/rest-logout/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-logout/"
			connection = requests.post(url, data = {'token':token})
		except requests.ConnectionError, e:
			connection = e
		return connection

	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		token = config.get('user_details', 'token')
		if token != "":
			connection = Logout.send_request(self,token)
			if connection.status_code == 204:
				config.set('user_details', 'username', "")
				config.set('user_details','token', "")
				config.set('user_details','current_directory',"")
				config.set('user_details','id',"")
				with open(filepath, 'w') as f:
					config.write(f)
				print "Deleted token and user account details."
			else:
				print connection
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authentication is compelete."


	
		