## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
from ConfigParser import SafeConfigParser
import json,requests
from os.path import expanduser
from _color import ax_blue

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
						data = json.loads(connection.text)    
						summary_file = data['message']
						status_code = data['status_code']
						#print summary_file
						print ax_blue(('\nProject Details:'))
						print ax_blue(('\n\t Project Name -  %s'%(summary_file['projectname'])))
						print ax_blue(('\n\t Admin - %s' %(summary_file['admin'])))
						print ax_blue(('\n\t Contributors -  %s' %(summary_file['contributors']))) 
						print ax_blue(('\n\t Project Files -  %s' %(summary_file['file_list'])))
						print ax_blue(('\n\t Project Folders - %s' %(summary_file['folder_list'])))
						print ('\n')
					else:
						print connection.text
				else:
					connection = Summary.send_request(self,token,env_flag,env_name)
					if connection.status_code == 200:
						data = json.loads(connection.text)     #["Kevin","yedid","kevin.yedid@gmail.com","5 GB","3M"]
						summary_file = data['message'] #[u'Kevin', u'yedid', u'kevin.yedid@gmail.com', u'5 GB', u'3M']
						status_code = data['status_code']
						#print summary_file
						print ax_blue(('\nAccount:'))
						print ax_blue(('\n\t User: %s %s' %(summary_file['firstname'], summary_file['lastname'])))
						print ax_blue(('\n\t Antarin ID: %s' %(summary_file['username'])))
						print ax_blue(('\n\t Storage Use: %s / %s' %(summary_file['data_storage_used'], summary_file['data_storage_available'])))
						print('\n')
					else:
						print connection.text
			else:
				error_flag=1
		if config.has_section('user_details') == False or error_flag==1:
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")


	