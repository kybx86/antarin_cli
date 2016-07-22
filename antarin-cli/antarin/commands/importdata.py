## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write

class ImportData(Base):

	def send_request(self,token,path,env_name,folder_flag):
		try:
			#url = "http://127.0.0.1:8000/rest-importdata/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-importdata/"
			connection = requests.post(url, data = {'token':token,'path':path,'env_name':env_name,'folder_flag':folder_flag})
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
			folder_flag = 0
			if token != "":
				if int(env_flag):
					if self.options['--file']:
						folder_flag = 0 
						path = json.loads(json.dumps(self.options))['<filename>']
						connection = ImportData.send_request(self,token,path,env_name,folder_flag)
						if connection.status_code!=204:
							print connection
					elif self.options['--folder']:
						folder_flag = 1
						path = json.loads(json.dumps(self.options))['<foldername>']
						connection = ImportData.send_request(self,token,path,env_name,folder_flag)
						if connection.status_code!=204:
							print connection
				else: #inside file system env
					print "Error: You are currently not inside a project environment--try 'ax loadproject <projectname>' to load a project environment"
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

	
		