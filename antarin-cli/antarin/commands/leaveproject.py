## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##

from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue
import sys,os

class LeaveProject(Base):
	def send_request(self,token,projectname):
		try:
			#url = "http://127.0.0.1:8000/rest-leaveproject/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-leaveproject/"
			
			connection = requests.post(url, data = {'token':token,'projectname':projectname})
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
					connection = LeaveProject.send_request(self,token,projectname)
					if connection.status_code==200:
						print connection.text
					else:
						print connection.text
				else:
					print "Error: You are inside a project environment. Please try this command after exiting the project--see 'ax exitproject'"
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

	
		