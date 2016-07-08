
from .base import Base
import getpass
import urllib2, urllib
import json
import sys,os

from antarin.config import write

class Login(Base):

	def verify(self,userdict):
		method = 'POST'
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-auth/login/"
		handler = urllib2.HTTPHandler()
		opener = urllib2.build_opener(handler)
		data = urllib.urlencode(userdict)
		request = urllib2.Request(url,data=json.dumps(userdict))
		request.add_header("Content-Type",'application/json')
		request.get_method = lambda:method
		try:
			connection = opener.open(request)
		except urllib2.HTTPError,e:
			connection = e
		return connection

	def run(self):
		userdict = {}
		print 'Enter your Antarin credentials'
		try:
			while 1 :
				userdict['username'] = str(raw_input('Username:'))
				userdict['password'] = getpass.getpass('Password:(will be hidden as you type)')
				connection = Login.verify(self,userdict)
				data = json.load(connection)
				if connection.code == 200:
					token = data['key']
					print 'Authentication Successful!'
					write("username",userdict['username'])
					write("token",token)
					break
				else:
					token = ""
					write("username",userdict['username'])
					write("token",token)
					print 'Invalid username and/or password'
		except KeyboardInterrupt:
			print("\n")
			try:
				sys.exit(0)
			except SystemExit:
				os._exit(0)
 		