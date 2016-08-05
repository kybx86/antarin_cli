## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from _color import ax_blue, bold

class NewInstance(Base):

	def send_request(self,token,instance_name,ami_id,instance_type,projectname,region):
		try:
			url = "http://127.0.0.1:8000/rest-newinstance/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-newinstance/"
			payload = {'token':token,'projectname':projectname, 'instance_name':instance_name,'ami_id':ami_id,'instance_type':instance_type,'region':region}
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
			env_flag = config.get('user_details','PROJECT_ENV')
			env_name = config.get('user_details','PROJECT_ENV_NAME')
			if token != "":
				if int(env_flag):
					instance_name = str(raw_input(ax_blue(bold('Instance Name: '))))
					ami_id = str(raw_input(ax_blue(bold('Machine Image ID (Ubuntu 14.04 - ami-d732f0b7): '))))
					instance_type = str(raw_input(ax_blue(bold('Instance Type (t2.micro): '))))
					region = str(raw_input(ax_blue(bold('Region (us-west-2):'))))

					connection = NewInstance.send_request(self, token, instance_name,ami_id,instance_type,env_name,region)
					data = json.loads(connection.text)    

					if connection.status_code == 200:
						#message = data['message']
						print(connection.text)
						#print ax_blue("\nCreated new project: '%s'" %(projectname))
					#elif connection.status_code == 400: #-- Project exists
					#	print ax_blue("\nError: A project with name '%s' already exists in your account. Please choose another name." %(projectname))
					elif connection.status_code == 404:
						print ax_blue('\nError: Session token is not valid')
					else:
					#	print ax_blue(connection)
						print ax_blue(connection.text) #--error cases not yet handled
				else:
					print ax_blue("\nError: Enter project to create an instance--see 'ax enterproject <projectid>'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		