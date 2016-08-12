## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##

from .base import Base
from ConfigParser import SafeConfigParser
import json,requests
from os.path import expanduser
from _color import ax_blue, bold, out



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
		error_flag = 0

		if config.has_section('user_details'):
			token = config.get('user_details', 'token')		
			if token != "":
				env_flag = config.get('user_details','PROJECT_ENV')
				env_name = config.get('user_details','PROJECT_ENV_NAME')
				if int(env_flag): #inside project env
					connection = Summary.send_request(self, token, env_flag, env_name)
					if connection.status_code == 200:
						data = json.loads(connection.text)    
						summary_file = data['message']
						status_code = data['status_code']
						project_name = summary_file['projectname'].split(':')[1]

						out(ax_blue(bold('\nProject Details:\n')))
						out(ax_blue(bold('\n\tProject Name: ')) + ax_blue(project_name))
						out(ax_blue(bold('\n\tAdmin: ')) + ax_blue(summary_file['admin']))
						#--iterating for fields that can contain variable length fields
						out(ax_blue(bold('\n\tContributors: \n')))
						for i in xrange(len(summary_file['contributors'])):
							username = summary_file['contributors'][i][0]
							user_status = summary_file['contributors'][i][1]
							print ax_blue("\t\t%s \t%s" %(username, user_status))

						out(ax_blue(bold('\tProject Files: \n')))
						for i in xrange(len(summary_file['file_list'])):
							filename = summary_file['file_list'][i][0]
							owner = summary_file['file_list'][i][1]
							print ax_blue("\t\t%s \t%s" %(owner, filename))
						
						out(ax_blue(bold('\tProject Folders: \n')))
						for i in xrange(len(summary_file['folder_list'])):
							foldername = summary_file['folder_list'][i][0]
							owner = summary_file['folder_list'][i][1]
							print ax_blue("\t\t%s \t%s" %(owner, foldername))
						
					elif connection.status_code == 404:
						print ('\nError: Project does not exist')
					else:
						print ax_blue(connection.text) #--error cases not yet handled
				else:
					connection = Summary.send_request(self, token, env_flag, env_name)
					if connection.status_code == 200:
						data = json.loads(connection.text)  
						summary_file = data['message']        
						status_code = data['status_code']
						
						out(ax_blue(bold('\nAccount:\n')))
						out(ax_blue(bold('\n\tUser: ')) + ax_blue(summary_file['firstname']) + " " + ax_blue(summary_file['lastname']))
						out(ax_blue(bold('\n\tAntarin ID: ')) + ax_blue(summary_file['username']))
						out(ax_blue(bold('\n\tStorage Use: '))), out(ax_blue('%s / %s' %(summary_file['data_storage_used'], summary_file['data_storage_available'])))
						out('\n')
					elif connection.status_code == 404:
						print ax_blue("\nError: Session token is not valid--see '$ ax login'")
					else:
						print ax_blue(connection.text) #--error cases not yet handled
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")


	