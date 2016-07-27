## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from _color import ax_blue

class RemoveObject(Base):
	def send_request(self,token,id_val,object_name,r_value,env_flag):
		payload = {'object_name':object_name,'id':id_val,'r_value':r_value,'token':token,'env_flag':env_flag}
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
		token = config.get('user_details', 'token')
		id_val = config.get('user_details','id')
		env_flag = config.get('user_details','PROJECT_ENV')
		if token != "":
			object_name = json.loads(json.dumps(self.options))['<folder/file>']
			if object_name[0] == '/':
				object_name = object_name[1:]
			r_value = json.loads(json.dumps(self.options))['-r']
			connection = RemoveObject.send_request(self,token,id_val,object_name,r_value,env_flag)

			if connection.status_code == 204:
				print ax_blue('\nDeleted ' + object_name) # succesfully deleting file 

			if connection.status_code == 404 or connection.status_code == 400:#  File/Folder does not exist
				#print ax_blue(json.loads(connection.text)) 
				# ^^^ "ERROR: File does not exist." <--- where is this .text coming from ?!
				# how about we define our own error message under the 404 and 400 conditions ? i.e.: 
				print ax_blue('Error: File %s does not exist' %(object_name))

			# elif connection.status_code == 400:# BAD REQUEST --Folder not empty
			# 	print json.loads(connection.text)
			elif connection.status_code!=204:
				print ax_blue(connection)
		else: 
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")
			