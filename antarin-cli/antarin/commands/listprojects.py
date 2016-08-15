## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from _color import ax_blue, bold, out


class ListAllProjects(Base):

	def send_request(self,token):
		try:
			url = "http://127.0.0.1:8000/rest-listallprojects/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-listallprojects/"
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
			username = config.get('user_details', 'username')
			if token != "":
				if int(env_flag)==0:
					connection = ListAllProjects.send_request(self,token)
					if connection.status_code == 200:
						message =  json.loads(connection.text)
						data = message['message']
					
						print ax_blue(bold('\nMy Projects:\n'))
						# this is split the return value given from views.py as: 
						# return_val.append(project.project.name+"\t"+status+"\t"+str(project.access_key))
						for i in xrange(0, len(data)):
							project_entry = data[i]
							project_entry = project_entry.split('\t') 
							project_name = project_entry[0].split(':')[1]
							out(ax_blue(bold('\tProject Name:\t') + ax_blue('{:12s}'.format(project_name[:12]))))
							out(ax_blue(bold('\tPermissions:\t') + ax_blue(project_entry[1])))
							out(ax_blue(bold('\tProject ID:\t') + ax_blue(project_entry[2])))
							out('\n')
								
					elif connection.status_code == 404:
						print ax_blue('\nError: Session token is not valid')
					else:
						print ax_blue(connection)
						print ax_blue(connection.text) #--error cases not yet handled

				else: #inside project environment
					print ax_blue("\nError: You need to exit from the current environment to see a list of all projects--see 'ax exitproject'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		