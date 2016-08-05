## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue


class EnterInstance(Base):

	def send_request(self,token,access_key):
		try:
			url = "http://127.0.0.1:8000/rest-enterinstance/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-enterinstance/"
			connection = requests.post(url, data = {'token':token,'access_key':access_key})
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
			instance_flag = config.get('user_details','INSTANCE_ENV')
			if token != "":
				if int(env_flag) == 1 and int(instance_flag)==0:
					access_key = json.loads(json.dumps(self.options))['<accesskey>']
					connection = EnterInstance.send_request(self, token, access_key)
					if connection.status_code == 200:
						write("INSTANCE_ENV",'1') #inside instance env
						data = json.loads(connection.text)['message']
						write("INSTANCE_ENV_ID", str(data['id']))
						instance_name = data['name']
						print ax_blue("\nEntered instance: '%s'" %(instance_name))
					elif connection.status_code == 400:
						print ax_blue("\nError: Instance with access code '%s' does not exist in your account. Please verify access code." %(access_key))
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

	
		