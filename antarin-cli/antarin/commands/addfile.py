## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json

class NewProject(Base):

	def send_request(self,token,projectname,filename,id_val):
		try:
			url = "http://127.0.0.1:8000/rest-addfiletoproject/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-addfiletoproject/"
			connection = requests.post(url, data = {'token':token,'projectname':projectname,'filename':filename,'id':id_val})
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
			id_val = config.get('user_details','id')
			if token != "":
				filename = json.loads(json.dumps(self.options))['<filename>']
				projectname = json.loads(json.dumps(self.options))['<projectname>']
				connection = NewProject.send_request(self,token,projectname,filename,id_val)
				if connection.status_code != 204:
					print connection
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

	
		