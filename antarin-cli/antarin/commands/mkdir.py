## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import json,requests
from _color import ax_blue

class MakeDirectory(Base):
	def send_request(self,token,id_val,foldername,env_flag,count_val=None,alt_foldername=None):
		
		try:
			#url = "http://127.0.0.1:8000/rest-mkdir/"
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-mkdir/"
			connection = requests.post(url, data = {'token':token,'foldername':foldername,'id':id_val,'env_flag':env_flag,'count':count_val,'alt_foldername':alt_foldername})
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
			id_val = config.get('user_details','id')
			env_flag = config.get('user_details','PROJECT_ENV')
			if token != "":
				foldername = json.loads(json.dumps(self.options))['<foldername>']
				if foldername[0] == '/':
					foldername = foldername[1:]
				connection = MakeDirectory.send_request(self, token, id_val, foldername, env_flag)

				if connection.status_code == 200: # Created dir succesfully 
					print ax_blue('\nCreated new directory %s' %(foldername))

				if connection.status_code == 400:#BAD REQUEST -- duplicate names
					#print json.loads(connection.text) 
					print ax_blue('Error: Folder %s already exists --Create with a different name' %(foldername))
				elif connection.status_code == 404:
					print ax_blue(connection.text)
				#else:
				#	print connection #this is printing: <Response [200]>, which is a success, so im going to comment it out
					
			else:
				error_flag = 1
		
		if config.has_section('user_details') == False or error_flag == 1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"


