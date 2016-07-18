from .base import Base
from ConfigParser import SafeConfigParser
import json, urllib2, urllib
from os.path import expanduser

class Summary(Base):
	def send_request(self,token):
		method = 'GET'
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-summary/"
		handler = urllib2.HTTPHandler()
		opener = urllib2.build_opener(handler)
		request = urllib2.Request(url,data=json.dumps(token))
		request.add_header("Content-Type",'application/json')
		request.get_method = lambda:method
		#print request
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
		if token != "":
			connection = Summary.send_request(self,token)
			#print connection
			if connection.code == 200:
				data = connection.read()
				for i in range(0,len(json.loads(data))):
					print json.loads(data)[i]
			else:
				print 'ERROR'
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authentication is compelete."


	