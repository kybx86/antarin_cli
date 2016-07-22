## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
from antarin.config import write
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
		error_flag=0

		if config.has_section('user_details'):
			token = config.get('user_details', 'token')
			if token != "":
				connection = Logout.send_request(self,token)
				if connection.status_code == 204:
					write("username",'')
					write("token",'')
					write("current_directory",'')
					write("id","")
					write("PROJECT_ENV",'')
					write("PROJECT_ENV_NAME",'')
					write("PID",'')
					write("RET_ID",'')
					print "Deleted token and user account details."
				else:
					print connection
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

	
		