from .base import Base
from ConfigParser import SafeConfigParser
import json, urllib2, urllib,os,requests
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

class Download(Base):

	def send_request(self,token):
		filename = json.loads(json.dumps(self.options))['<file>']
		url = "http://127.0.0.1:8000/rest-filedownload/"
		files = {
			'token' : (None, json.dumps(token), 'application/json'),
         	'file': (None, json.dumps(filename), 'application/json')
		}
		#print files
		try:
			connection = requests.get(url, files=files)
		except:
			connection = None
		return connection

	def run(self):
		config = SafeConfigParser()
		config.read('config.ini')
		token = config.get('user_details', 'token')
		if token != "":
			connection = Download.send_request(self,token)
			print json.load(connection)
			# filename = json.loads(json.dumps(self.options))['<file>']
			# url = "https://s3-us-west-2.amazonaws.com/antarin-test/media/user_files" + filename
			# val = urlretrieve(url,"./downloads/"+filename)
			# print val
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."