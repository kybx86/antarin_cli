## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json,sys
from antarin.config import write
from _color import ax_blue, bold, out

class LaunchInstance(Base):

	def send_request(self,token,access_key,command_flag):
		try:
			url = "http://127.0.0.1:8000/rest-launchinstance/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-launchinstance/"
			connection = requests.post(url, data = {'token':token,'access_key':access_key,'command_flag':command_flag})
		except requests.ConnectionError, e:
			connection = e
		return connection

	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		error_flag = 0
		command_flag = 0
		if config.has_section('user_details'):
			token = config.get('user_details', 'token')
			env_flag = config.get('user_details','PROJECT_ENV')
			instance_flag = config.get('user_details','INSTANCE_ENV')
			if token != "":
				if int(env_flag) == 1 and int(instance_flag)==0:
					access_key = json.loads(json.dumps(self.options))['<accesskey>']
					connection = LaunchInstance.send_request(self, token, access_key,command_flag)
					if connection.status_code == 200:
						print connection.text
						try:
							while True:
								command = str(raw_input(ax_blue(bold('>>'))))
								if 'install' in command or 'exit' in command:
									command_flag = 1
									c = LaunchInstance.send_request(self,token,access_key,command_flag)
									print c.connection.text
								else:
									print 'Not a valid command'

						except KeyboardInterrupt:
							print("\n")
							try:
								sys.exit(0)
							except SystemExit:
								os._exit(0)	

					elif connection.status_code == 400:
						print ax_blue("\nError: Instance with access code '%s' does not exist in your account. Please verify access code." %(access_key))
					else:
						print connection.text
				elif int(instance_flag) == 1:
					print ax_blue("\nError: You are currently inside an instance environemnt--see 'ax exitinstance'") 
				elif int(env_flag) == 0: #not inside project environment
					print ax_blue("\nError: Enter project to load an instance--see 'ax enterproject <projectid>'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		