## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue


class LoadProject(Base):

	def send_request(self,token,projectid):
		try:
			#url = "http://127.0.0.1:8000/rest-loadproject/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-loadproject/"
			connection = requests.post(url, data = {'token':token,'projectid':projectid})
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
					projectid = json.loads(json.dumps(self.options))['<projectid>']
					connection = LoadProject.send_request(self,token,projectid)
					if connection.status_code == 200:
						write("PROJECT_ENV",'1')
						data = json.loads(connection.text)['message']
						write("PROJECT_ENV_NAME",data['projectname'])
						#nameval = projectname.split(':')[1]
						
						print data
						print ax_blue('\nEntered Project %s' %(data['projectname']))
						####TODO:customize shell prompt with nameval
					else:
						print ax_blue(json.loads(connection.text))
				else: #inside project environment
					print ax_blue("Error: You need to exit from the current environment to load a new project--see 'ax exitproject'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		