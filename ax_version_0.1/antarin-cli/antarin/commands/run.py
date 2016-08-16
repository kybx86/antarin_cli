## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json,sys
from antarin.config import write
from _color import ax_blue, bold, out

class RunCommand(Base):

	def send_request(self,token,env_name,instance_id,package_name,shell_command):
		try:
			url = "http://127.0.0.1:8000/rest-runcommand/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-runcommand/"
			connection = requests.post(url, data = {'token':token,'projectname':env_name,'instance_id':instance_id,'packagename':package_name,'shell_command':shell_command})
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
			instance_flag = config.get('user_details','INSTANCE_ENV')
			instance_id = config.get('user_details','INSTANCE_ENV_ID')
			if token != "":
				if int(env_flag) == 1 and int(instance_flag) == 1:
					shell_command = json.loads(json.dumps(self.options))['<shell_command>']
					package_name = json.loads(json.dumps(self.options))['<packagename>']
					connection = RunCommand.send_request(self, token,env_name,instance_id,package_name,shell_command)
					if connection.status_code == 200:
						data = json.loads(connection.text)    
						message = data['message']
						for item in message:
							print ax_blue(item)
					elif connection.status_code == 400:
						print ax_blue("\nError: Package name '%s' does not exist in your account" %(package_name))
					else:
						print connection.text
				elif int(instance_flag) == 0:
					print ax_blue("\nError: You are not inside a cloud environemnt--see 'ax entercloud <accesskey>'") 
				elif int(env_flag) == 0: #not inside project environment
					print ax_blue("\nError: Enter project to load an instance--see 'ax enterproject <projectid>'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		