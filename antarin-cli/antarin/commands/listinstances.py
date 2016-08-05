## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue


class ListInstances(Base):

	def send_request(self,token,projectname):
		try:
			url = "http://127.0.0.1:8000/rest-listallinstances/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-listallinstances/"
			connection = requests.post(url, data = {'token':token,'projectname':projectname})
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
			projectname = config.get('user_details','PROJECT_ENV_NAME')
			instance_flag = config.get('user_details','INSTANCE_ENV')
			if token != "":
				if int(env_flag) and int(instance_flag)==0:
					connection = ListInstances.send_request(self, token, projectname)
					if connection.status_code == 200:
						print(connection.text)
					#elif connection.status_code == 404:
					#	print ax_blue("\nError: Instance with access code '%s' does not exist in your account. Please verify access code." %(access_key))
					else:
						print ax_blue(json.loads(connection.text)) 
				elif int(instance_flag) == 1:
					print ax_blue("\nError: You are currently inside an instance environemnt--see 'ax exitinstance'") 
				elif int(env_flag) == 0: #not inside project environment
					print ax_blue("\nError: Enter project to load an instance--see 'ax enterproject <projectid>'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		