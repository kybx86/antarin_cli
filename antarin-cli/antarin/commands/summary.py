## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
from ConfigParser import SafeConfigParser
import json,requests
from os.path import expanduser

class Summary(Base):
	def send_request(self,token,env_flag,env_name):
		#url = "http://127.0.0.1:8000/rest-summary/"
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-summary/"
		payload = {'token':token,'env_flag':env_flag,'env_name':env_name}
		try:
			connection = requests.post(url, data = payload)
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
			if token != "":
				env_flag = config.get('user_details','PROJECT_ENV')
				env_name = config.get('user_details','PROJECT_ENV_NAME')
				if int(env_flag): #inside project env
					connection = Summary.send_request(self,token,env_flag,env_name)
					if connection.status_code == 200:
						data = connection.text    
						summary_file = json.loads(data)
						print('\nProject Details:')
						print('\n\t Project Name -  %s'%(summary_file['projectname']))
						print('\n\t Admin - %s' %(summary_file['admin']))
						print('\n\t Contributors -  %s' %(summary_file['contributors']))
						print('\n\t Project Files -  %s' %(summary_file['file_list']))
						print('\n\t Project Folders - %s' %(summary_file['folder_list']))
						print('\n')
					else:
						print connection
				else:
					connection = Summary.send_request(self,token,env_flag,env_name)
					if connection.status_code == 200:
						data = connection.text     #["Kevin","yedid","kevin.yedid@gmail.com","5 GB","3M"]
						summary_file = json.loads(data) #[u'Kevin', u'yedid', u'kevin.yedid@gmail.com', u'5 GB', u'3M']
						print('\nAccount:')
						print('\n\t User: %s %s' %(summary_file[0], summary_file[1]))
						print('\n\t Antarin ID: %s' %(summary_file[2]))
						print('\n\t Storage Use: %s / %s' %(summary_file[4], summary_file[3]))
						print('\n')
					else:
						print connection
			else:
				error_flag=1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"


	