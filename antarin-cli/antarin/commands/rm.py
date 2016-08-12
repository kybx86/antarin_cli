## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from _color import ax_blue

class RemoveObject(Base):
	def send_request(self,token,id_val,object_name,r_value,env_flag,env_name):
		payload = {'object_name':object_name,'id':id_val,'r_value':r_value,'token':token,'env_flag':env_flag,'env_name':env_name}
		#url = "http://127.0.0.1:8000/rest-rm/"
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-rm/"
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
				object_name = json.loads(json.dumps(self.options))['<folder/file>']
				if object_name[0] == '/':
					object_name = object_name[1:]
				r_value = json.loads(json.dumps(self.options))['-r']

				connection = RemoveObject.send_request(self, token, id_val, object_name, r_value, env_flag, env_name)

				if connection.status_code == 204:
					print ax_blue('\nDeleted ' + object_name) #--succesfully deleting file
					#print ax_blue(connection.text) 
				elif connection.status_code == 400: #--file/Folder does not exist
					print ax_blue("\nError: 'ax rm -r <foldername>' is only valid to delete entire folders, not files")
					#print ax_blue(connection.text)
				elif connection.status_code == 404: #--wrong usage of rm 
					print ax_blue("\nError: This file/folder may not exist or folder may contain other files--see 'ax rm -r <foldername>'")
					#print ax_blue(connection.text)
				else:
					print ax_blue(connection.text) #--error cases not yet handled
			else:
				error_flag = 1

		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")




			