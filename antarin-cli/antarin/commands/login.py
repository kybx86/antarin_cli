## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
import getpass
import urllib2, urllib
import json
import sys,os
from ConfigParser import SafeConfigParser
from antarin.config import write
from os.path import expanduser
from _color import ax_blue, bold, out

class Login(Base):

	def verify(self,userdict):
		method = 'POST'
		#url = "http://127.0.0.1:8000/rest-auth/login/"
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-auth/login/"
		handler = urllib2.HTTPHandler()
		opener = urllib2.build_opener(handler)
		data = urllib.urlencode(userdict)
		request = urllib2.Request(url,data=json.dumps(userdict))
		request.add_header("Content-Type",'application/json')
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
			

		if config.has_section('user_details') and config.get('user_details', 'token') == "":
			out(ax_blue(bold('\nEnter your Antarin credentials\n')))
			try:
				while 1 :
					
					userdict['username'] = str(raw_input(ax_blue(bold('Antarin ID: '))))
					userdict['password'] = getpass.getpass(ax_blue(bold('Password:(will be hidden as you type) ')))
					connection = Login.verify(self,userdict)
					data = json.load(connection)
					if connection.code == 200:
						token = data['key']
						print ax_blue('\nantarinX login succesful!\n')
						print ax_blue('Logged in as: %s' %userdict['username'])
						print ax_blue('Session Token: %s' %token)
						write("username",userdict['username'])
						write("token",token)
						write("current_directory",'~antarin')
						write("id","")
						write("PROJECT_ENV",'0')
						write("PROJECT_ENV_NAME",'')
						write("PID",'')
						write("RET_ID",'')
						write("INSTANCE_ENV",'0')
						break
					else:
						token = ""
						write("username",userdict['username'])
						write("token",token)
						write("current_directory",'')
						write("id","")
						write("PROJECT_ENV",'')
						write("PROJECT_ENV_NAME",'')
						write("PID",'')
						write("RET_ID",'')
						write("INSTANCE_ENV",'')
						print ax_blue('Invalid username and/or password\n')
			except KeyboardInterrupt:
				print("\n")
				try:
					sys.exit(0)
				except SystemExit:
					os._exit(0)

		elif config.has_section('user_details') == False:
			out(ax_blue(bold('\nEnter your Antarin credentials\n')))
			try:
				while 1 :
					userdict['username'] = str(raw_input(ax_blue(bold('Antarin ID:')))) 
					userdict['password'] = getpass.getpass(ax_blue(bold('Password:(will be hidden as you type) ')))
					connection = Login.verify(self,userdict)
					data = json.load(connection)
					if connection.code == 200:
						token = data['key']
						print ax_blue('\nantarinX login succesful!\n')
						print ax_blue('Logged in as: %s' %userdict['username'])
						print ax_blue('Session Token: %s' %token)
						write("username",userdict['username'])
						write("token",token)
						write("current_directory",'~antarin')
						write("id","")
						write("PROJECT_ENV",'0')
						write("PROJECT_ENV_NAME",'')
						write("PID",'')
						write("RET_ID",'')
						write("INSTANCE_ENV",'0')
						break
					else:
						token = ""
						write("username",userdict['username'])
						write("token",token)
						write("current_directory",'')
						write("id","")
						write("PROJECT_ENV",'')
						write("PROJECT_ENV_NAME",'')
						write("PID",'')
						write("RET_ID",'')
						write("INSTANCE_ENV",'')
						print ax_blue('\nInvalid username and/or password\n')
			except KeyboardInterrupt:
				print("\n")
				try:
					sys.exit(0)
				except SystemExit:
					os._exit(0)

		elif config.get('user_details', 'token') != "":

			print ax_blue('\nLogged in as: %s' %config.get('user_details', 'username'))
			print ax_blue('Session Token: %s' %config.get('user_details', 'token'))
 		