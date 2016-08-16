## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue

class ExitCloud(Base):

	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		error_flag=0

		if config.has_section('user_details'):
			token = config.get('user_details', 'token')
			instance_flag = config.get('user_details','INSTANCE_ENV')
			if token != "":
				if int(instance_flag):
					write("INSTANCE_ENV",'0')
					write("INSTANCE_ENV_ID",'')
					print ax_blue("\nExited cloud")
					####TODO:customize shell prompt 
				else: #inside file system environment
					print ax_blue("Error: You are currently not inside an instance environment--try 'ax enterinstance <accesskey>' to load a project environment")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		