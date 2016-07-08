from .base import Base
from ConfigParser import SafeConfigParser
import json, urllib2, urllib

class Ls(Base):

	def run(self):

		config = SafeConfigParser()
		config.read('config.ini')
		token = config.get('user_details', 'token')
		if token != "":
			method = 'GET'
			url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-summary/"
			handler = urllib2.HTTPHandler()
			opener = urllib2.build_opener(handler)
			request = urllib2.Request(url,data=json.dumps(token))
			request.add_header("Content-Type",'application/json')
			request.get_method = lambda:method
			try:
				connection = opener.open(request)
			except urllib2.HTTPError,e:
				connection = e
		
			if connection.code == 200:
				data = connection.read()
				#print len(json.loads(data))
				for i in range(0,len(json.loads(data))):
					print json.loads(data)[i]
				#file = json.load(connection)
				#print file
			else:
				print 'Error while fetching files'

		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."
