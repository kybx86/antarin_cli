
from .base import Base
import getpass
import urllib2, urllib
import json
import sys,os
from ConfigParser import SafeConfigParser
from antarin.config import write
from os.path import expanduser

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
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		token = config.get('user_details', 'token')
		username = config.get('user_details','username')
		if token == "":
			print '\nEnter your Antarin credentials'
			try:
				while 1 :
					userdict['username'] = str(raw_input('Username:'))
					userdict['password'] = getpass.getpass('Password:(will be hidden as you type)')
					connection = Login.verify(self,userdict)
					data = json.load(connection)
					if connection.code == 200:
						token = data['key']
						print 'Logged in as: %s' %userdict['username']
						print 'Token used for authentication : %s\n' %token
						write("username",userdict['username'])
						write("token",token)
						write("current_directory",'/')
						write("id","")
						break
					else:
						token = ""
						write("username",userdict['username'])
						write("token",token)
						write("current_directory",'')
						write("id","")
						print 'Invalid username and/or password\n'
			except KeyboardInterrupt:
				print("\n")
				try:
					sys.exit(0)
				except SystemExit:
					os._exit(0)
		else:
			print 'Logged in as: %s' %username
			print 'Token: %s' %token
 		