from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json

class RemoveObject(Base):
	def send_request(self,token,id_val,object_name,r_value):
		payload = {'object_name':object_name,'id':id_val,'r_value':r_value,'token':token}
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

		if token != "":
			object_name = json.loads(json.dumps(self.options))['<folder/file>']
			r_value = json.loads(json.dumps(self.options))['-r']
			connection = RemoveObject.send_request(self,token,id_val,object_name,r_value)
			if connection.status_code != 204:
				print connection
		else: 
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"
			