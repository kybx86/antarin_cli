## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from _color import ax_blue 

class NewProject(Base):

	def send_request(self,token,projectname):
		try:
			#url = "http://127.0.0.1:8000/rest-newproject/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-newproject/"
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
					####TODO:Projectname validation (Make sure it does not contain a ':')
					connection = NewProject.send_request(self,token,projectname)
					if connection.status_code == 200:
						data = connection.text
						#print "New project created as - "+ json.loads(data)
						print ax_blue('\nCreated new project: %s' %(json.loads(data)))
					elif connection.status_code == 400: #Project exists
						print json.loads(connection.text)
				else:
					print ax_blue("Error: You need to exit from the current project to create a new project--see 'ax exitproject'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		