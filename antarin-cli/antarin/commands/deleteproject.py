## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
import getpass
from antarin.config import write
from _color import ax_blue
import sys,os

class DeleteProject(Base):

	def exit(self):
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)

	def check_permissions(self,token,projectname):
		try:
			#url = "http://127.0.0.1:8000/rest-deleteproject/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-deleteproject/"
			connection = requests.get(url, data = {'token':token,'projectname':projectname})
		except requests.ConnectionError, e:
			connection = e
		return connection

	def send_request(self,entered_password,token,projectname):
		try:
			#url = "http://127.0.0.1:8000/rest-deleteproject/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-deleteproject/"
			
			connection = requests.post(url, data = {'token':token,'projectname':projectname,'pwd':entered_password})
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
			env_flag = config.get('user_details','PROJECT_ENV')
			env_name = config.get('user_details','PROJECT_ENV_NAME')
			if token != "":
				if int(env_flag)==0:
					projectname = json.loads(json.dumps(self.options))['<projectname>']
					connection = DeleteProject.check_permissions(self,token,projectname)
					if connection.status_code==200:
						try:
							while 1:
								user_input = str(raw_input(ax_blue("\nAre you sure you want to delete this project and all the data associated with it? (yes/no) ")))
								if user_input == "yes":
									entered_password = getpass.getpass(ax_blue('Enter your antarinX password:(will be hidden as you type) '))
									connection = DeleteProject.send_request(self,entered_password,token,projectname)
									if connection.status_code == 200: #verification successful and project deleted
										print connection.text
										break
									else:
										print connection.text
										DeleteProject.exit(self)
								elif user_input == "no":
									break
									DeleteProject.exit(self)
								else:
									print ax_blue("Your response was not one of the expected responses (yes/no).")
						except KeyboardInterrupt:
							print("\n")
							DeleteProject.exit(Self)
					else:
						print connection.text
				else:
					print "Error: You are inside a project environment. Please try this command after exiting the project--see 'ax exitproject'"
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

	
		