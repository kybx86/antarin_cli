## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue

class AddContributor(Base):

	def send_request(self,token,username,env_name):
		try:
			#url = "http://127.0.0.1:8000/rest-addcontributor/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-addcontributor/"
			connection = requests.post(url, data = {'token':token,'username':username,'env_name':env_name})
		except requests.ConnectionError, e:
			connection = e
		return connection

	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		error_flag = 0

		if config.has_section('user_details'):
			token = config.get('user_details', 'token')
			env_flag = config.get('user_details','PROJECT_ENV')
			env_name = config.get('user_details','PROJECT_ENV_NAME')
			if token != "":
				if int(env_flag):
					username = json.loads(json.dumps(self.options))['<username>']
					connection = AddContributor.send_request(self, token, username, env_name)

					if connection.status_code == 200:
						print ax_blue("\nAdded contributor: '%s'" %(username))
					elif connection.status_code == 404:
						print ax_blue("\nError: Specified user '%s' is already a contributor to this project, or user does not exist" %(username))
					else:
						print ax_blue(json.loads(connection.text))
				else: #inside file system env
					print ax_blue("\nError: You are currently not inside a project environment--try 'ax loadproject <projectname>' to load a project environment")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		