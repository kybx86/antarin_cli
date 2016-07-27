## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from . import Base
from ConfigParser import SafeConfigParser
from os.path import expanduser
import requests,json
from antarin.config import write
from _color import ax_blue

class ExitProject(Base):

	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		error_flag=0

		if config.has_section('user_details'):
			token = config.get('user_details', 'token')
			env_flag = config.get('user_details','PROJECT_ENV')
			env_name = config.get('user_details','PROJECT_ENV_NAME')
			if token != "":
				if int(env_flag):
					write("PROJECT_ENV",'0')
					write("PROJECT_ENV_NAME",'')
					print ax_blue('\nExited project %s' %(env_name))
					####TODO:customize shell prompt 
				else: #inside file system environment
					print ax_blue("Error: You are currently not inside a project environment--try 'ax loadproject <projectname>' to load a project environment")
			else:
				error_flag = 1
		if config.has_section('user_details') == False or error_flag==1:
			print ax_blue("Error: You are not logged in. Please try this command after authentication--see 'ax login'")

	
		