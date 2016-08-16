## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
import getpass
import urllib2, urllib
import json
import sys,os
from ConfigParser import SafeConfigParser
from antarin.config import write
from os.path import expanduser
from _color import ax_blue


#we need to come up with a better way to use this command--and wonder if we even need it, given that we can get the 
# "(env) kevinyedid $" bash prompt going 


# i am not modifying this because future changes possible 
class Env(Base):
	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		error_flag=0

		if config.has_section('user_details'):
			token = config.get('user_details', 'token')
			if token != "":
				env_flag = config.get('user_details','PROJECT_ENV')
				env_name = config.get('user_details','PROJECT_ENV_NAME')
				instance_flag = config.get('user_details','INSTANCE_ENV')
				if int(env_flag) and int(instance_flag)==0:
					print "Inside Project - " + env_name
				elif int(env_flag) and int(instance_flag):
					print "Inside cloud "
				elif int(env_flag)==0 and int(instance_flag)==0:
					print "Inside file system env"
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

	