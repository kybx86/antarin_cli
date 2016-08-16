## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##

from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue
import os

class LeaveProject(Base):
	def send_request(self,token,projectid):
		try:
			url = "http://127.0.0.1:8000/rest-leaveproject/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-leaveproject/"
			
			connection = requests.post(url, data = {'token':token,'projectid':projectid})
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
					connection = LeaveProject.send_request(self,token,projectid)
					if connection.status_code == 200:
						print ax_blue("\nYou have been removed from project '%s' as contributor")
					elif connection.status_code == 400:
						print ax_blue("\nError: You cannot leave this project either because you are the Admin or because you do not belong to it")
					else:
						print ax_blue(connection.text)
				else:
					print ax_blue("\nError: You are inside a project environment. Please try this command after exiting the project--see 'ax exitproject'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		