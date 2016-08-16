## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue

class ChangeDirectory(Base):
	def send_request(self,token,id_val,env_flag,pid,env_name,retid_val):
		foldername = json.loads(json.dumps(self.options))['<foldername>']
		if foldername[0] == '/':
			foldername = foldername[1:]
		try:
			url = "http://127.0.0.1:8000/rest-cd/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-cd/"
			connection = requests.post(url, data = {'token':token,'foldername':foldername,'id':id_val,'env_flag':env_flag,'pid':pid,'env_name':env_name,'ret_id':retid_val})
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
				env_flag = int(config.get('user_details','PROJECT_ENV'))
				env_name = config.get('user_details','PROJECT_ENV_NAME')
				pid_val = config.get('user_details','PID')
				retid_val = config.get('user_details','RET_ID')
				if self.options['<foldername>'] is None or self.options['<foldername>'] == home_path:
					if env_flag == 0:
						write("current_directory",'~antarin')
						write("id",'')
					else:
						write("pid",'')
						write("rid",'') # <-- whats this ?
				else:
					connection = ChangeDirectory.send_request(self, token, id_val, env_flag, pid_val, env_name, retid_val)
					if connection.status_code == 200:	

						data = json.loads(connection.text)
						message = json.loads(data['message'])
						status_code = data['status_code']

						if env_flag == 0:
							current_directory = message['current_directory']
							id_val = message['id']
							write("current_directory", current_directory)
							write("id", str(id_val))
						else:
							pid_val = message['pid']
							write("pid", str(pid_val))
							write("ret_id", str(ret_id))
					else:
						#print ax_blue(json.loads(connection.text)) #ERROR: Folder does not exist.
						print ax_blue('\nError: Directory does not exist')
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag == 1:
			print ax_blue("\nError: You are not logged in. Please try this command after authentication--see 'ax login'")

