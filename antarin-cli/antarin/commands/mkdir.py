from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import json,requests

class MakeDirectory(Base):
	def send_request(self,token,id_val):
		foldername = json.loads(json.dumps(self.options))['<foldername>']
		try:
			connection = requests.post('http://webapp-test.us-west-2.elasticbeanstalk.com/rest-mkdir/', data = {'token':token,'foldername':foldername,'id':id_val})
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
		if token != "":
			connection = MakeDirectory.send_request(self,token,id_val)
			if connection.status_code != 204:
				print connection
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."


