from .base import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json

class RemoveObject(Base):
	def send_request(self,token):
		
		try:
			connection = opener.open(request)
		except urllib2.HTTPError,e:
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
			print object_name,r_value
		else: 
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"
			