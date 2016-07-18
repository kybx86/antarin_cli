from .base import Base
from ConfigParser import SafeConfigParser
import json, requests
from os.path import expanduser

class Ls(Base):

	def send_request(self,token,id_val):
		#url = "http://127.0.0.1:8000/rest-ls/"
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-ls/"
		payload = {'token':token,'id':id_val}
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
			connection = Ls.send_request(self,token,id_val)
			if connection.status_code == 200:
				data =  connection.text
				for i in range(0,len(json.loads(data))):
					print json.loads(data)[i]
			else:
				print 'Error while fetching files'

		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."
