from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json

class ChangeDirectory(Base):
	def send_request(self,token,id_val):
		foldername = json.loads(json.dumps(self.options))['<foldername>']
		try:
			#print foldername
			url = "http://127.0.0.1:8000/rest-cd/"
			#url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-cd/"
			connection = requests.post(url, data = {'token':token,'foldername':foldername,'id':id_val})
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
		#print self.options['foldername']
		if token != "":
			if self.options['<foldername>'] is None:
				config.set('user_details','current_directory','/')
				config.set('user_details','id','')
				with open(filepath, 'w') as f:
					config.write(f)
			else:
				connection = ChangeDirectory.send_request(self,token,id_val)
				if connection.status_code == 200:
					data = json.loads(json.loads(connection.text))
					current_directory = data['current_directory']
					id_val = data['id']
					config.set('user_details','current_directory',current_directory)
					config.set('user_details','id',str(id_val))
					with open(filepath, 'w') as f:
						config.write(f)
				else:
					print connection
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."


