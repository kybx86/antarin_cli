## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue

class AddToCloud(Base):

	def send_request(self,token,env_name,instance_id,section,packagename,path,filename):
		try:
			url = "http://127.0.0.1:8000/rest-adddata/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-adddata/"
			connection = requests.post(url, data = {'token':token,'path':path,'env_name':env_name,'instance_id':instance_id,'section':section,'packagename':packagename,'filename':filename})
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
			env_name = config.get('user_details','PROJECT_ENV_NAME')
			instance_flag = config.get('user_details','INSTANCE_ENV')
			instance_id = config.get('user_details','INSTANCE_ENV_ID')
			if token != "":
				if int(env_flag) and int(instance_flag):
					filename = ''
					path = ''
					packagename = ''
					if self.options['--env']:
						section = 'package'
						packagename = json.loads(json.dumps(self.options))['<packagename>']
					else:
						path = 	json.loads(json.dumps(self.options))['<path_in_package>']
						filename = json.loads(json.dumps(self.options))['<filename>']
						if self.options['--algo']:
							section='algo'	
						elif self.options['--data']:
							section='data'		
					
					connection = AddToCloud.send_request(self,token,env_name,instance_id,section,packagename,path,filename)
					if connection.status_code == 200: # successs
						print ax_blue("\nAdded file/package ")
					else: 
						print ax_blue('\n%s'%(json.loads(connection.text)))
				elif int(instance_flag)==0:
					print ax_blue("\nError: You are currently not inside an instance environment--see 'ax enterinstance <accesskey>'")
				elif int(env_flag)==0: #inside file system env
					print ax_blue("\nError: You are currently outside a project environment--see 'ax enterproject <projectid>' to access a project environment")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		