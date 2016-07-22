## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write

class LoadProject(Base):

	def send_request(self,token,projectname):
		try:
			#url = "http://127.0.0.1:8000/rest-loadproject/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-loadproject/"
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
			if token != "":
				if int(env_flag)==0:
					projectname = json.loads(json.dumps(self.options))['<projectname>']
					connection = LoadProject.send_request(self,token,projectname)
					if connection.status_code == 204:
						write("PROJECT_ENV",'1')
						write("PROJECT_ENV_NAME",projectname)
						nameval = projectname.split(':')[1]
						####TODO:customize shell prompt with nameval
					else:
						print connection
				else: #inside project environment
					print "Error: You need to exit from the current environment to load a new project--try 'ax exitproject'"
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

	
		