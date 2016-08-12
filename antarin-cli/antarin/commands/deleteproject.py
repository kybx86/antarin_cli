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

	def check_permissions(self, token, projectid):
		try:
			#url = "http://127.0.0.1:8000/rest-deleteproject/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-deleteproject/"
			connection = requests.get(url, data = {'token':token,'projectid':projectid})
		except requests.ConnectionError, e:
			connection = e
		return connection

	def send_request(self, entered_password, token, projectid):
		try:
			#url = "http://127.0.0.1:8000/rest-deleteproject/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-deleteproject/"
			
			connection = requests.post(url, data = {'token':token,'projectid':projectid,'pwd':entered_password})
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
			
			if token != "":
				if int(env_flag) == 0:
					projectid = json.loads(json.dumps(self.options))['<projectid>']
					connection = DeleteProject.check_permissions(self,token,projectid)
					if connection.status_code == 200:
						try:
							while 1:
								user_input = str(raw_input(ax_blue("\nAre you sure you want to delete this project and all the data associated with it? (yes/no) ")))
								if user_input == "yes":
									entered_password = getpass.getpass(ax_blue('Enter your antarinX password:(will be hidden as you type) '))
									connection = DeleteProject.send_request(self, entered_password, token, projectid)
									if connection.status_code == 200: #verification successful and project deleted
										#print connection.text
										print ax_blue("\nProject deleted from antarinX")
										break
									elif connection.status_code == 400:
										print ax_blue('\nError: Invalid password')
									else:
										print ax_blue(connection.text)
										DeleteProject.exit(self)
								elif user_input == "no":
									break
									DeleteProject.exit(self)
								else:
									print ax_blue("Invalid response. Please type 'yes' or 'no'")
						except KeyboardInterrupt:
							print("\n")
							DeleteProject.exit(self)
					else:
						print connection.status_code
				else:
					print ax_blue("\nError: You are inside a project environment. Please try this command after exiting the project--see 'ax exitproject'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		