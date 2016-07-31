## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
from ConfigParser import SafeConfigParser
import json, requests
from os.path import expanduser
from _color import ax_blue

class Ls(Base):

	def send_request(self,token,id_val,env_flag,env_name,pid_val):
		#url = "http://127.0.0.1:8000/rest-ls/"
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-ls/"
		payload = {'token':token,'id':id_val,'env_flag':env_flag,'env_name':env_name,'pid':pid_val}
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
				id_val = config.get('user_details','id')
				env_flag = config.get('user_details','PROJECT_ENV')
				env_name = config.get('user_details','PROJECT_ENV_NAME')
				pid_val = config.get('user_details','PID')
				connection = Ls.send_request(self,token,id_val,env_flag,env_name,pid_val)
				
				if connection.status_code == 200:
					data =  json.loads(connection.text)
					message = data['message']
					status_code = data['status_code']

					print ax_blue(('\nMy files:\n'))
					for i in range(0,len(message)):
						print ax_blue('\t' + message[i])
				elif connection.status_code == 404:
					print ('\nError: Session token is not valid')
				else:
					print ax_blue(connection)
					print ax_blue(connection.text) #--error cases not yet handled
			else:
				error_flag = 1

		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")
