## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json

class ListAllProjects(Base):

	def send_request(self,token):
		try:
			#url = "http://127.0.0.1:8000/rest-listallprojects/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-listallprojects/"
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
			env_flag = config.get('user_details','PROJECT_ENV')
			if token != "":
				if int(env_flag)==0:
					connection = ListAllProjects.send_request(self,token)
					if connection.status_code == 200:
						data =  connection.text
						for i in range(0,len(json.loads(data))):
							print json.loads(data)[i]
					else:
						print connection
				else: #inside project environment
					print "Error: You need to exit from the current environment to see a list of all projects--try 'ax exitproject'"
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

	
		