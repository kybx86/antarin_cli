## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json,sys,os
from _color import ax_blue, bold

class NewCloud(Base):

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
					try:
						instance_name = json.loads(json.dumps(self.options))['<name>']
						ami_id = str(raw_input(ax_blue(bold('Machine Image ID (AntarinX Linux AMI - ami-bd01cbdd): '))))
						instance_type = str(raw_input(ax_blue(bold('Instance Type (t2.micro): '))))
						region = str(raw_input(ax_blue(bold('Region (us-west-2):'))))

						connection = NewCloud.send_request(self, token, instance_name,ami_id,instance_type,env_name,region)
						data = json.loads(connection.text)    
						message = data['message']
						status_code = data['status_code']
						access_key_val = data['access_key']
						if connection.status_code == 200:
							print ax_blue(message + ' with access key: '+ str(access_key_val))					
						elif connection.status_code == 404:
							print ax_blue('\nError: Session token is not valid')
						else:
							print ax_blue(connection.text) #--error cases not yet handled
					except KeyboardInterrupt:
						print("\n")
						try:
							sys.exit(0)
						except SystemExit:
							os._exit(0)
				else:
					print ax_blue("\nError: Enter project to create an instance--see 'ax enterproject <projectid>'")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		