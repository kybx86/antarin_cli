"""
	antarinX configuration requirements
"""
#This file contains all configuration requirements of antarinX - API URL and the read,write methods 
#for configuration file maintained in the location - '~/.antarinx.config'

import os
import sys
import json
try:
	import ConfigParser as cparser # python 2.7
except ImportError:
	import configparser as cparser # python 3.5
from .utils import iocalls

URL = 'http://127.0.0.1:8000' # -- Localhost
#URL = 'http://http://webapp-test.us-west-2.elasticbeanstalk.com' # -- EB server

file_name = '.'+'axconfig'+'.ini'
config_file_path = os.path.join(os.path.expanduser('~'),file_name)

section_name = 'user_details'

class Config(cparser.SafeConfigParser):
	def __init__(self):
		self.file_path = config_file_path
		self.section_name = section_name
		super(Config,self).__init__()

	def get_file_path(self):
		return self.file_path

	def config_has_section(self):
		self.read_config()
		return super(Config,self).has_section(self.section_name)

	def add_section_to_config(self):
		super(Config,self).add_section(self.section_name)

	def read_config(self):
		return super(Config,self).read(self.file_path)

	def get_values(self):
		return (self._sections)[self.section_name]

	def get_val_from_config(self,item):
		try:
			self.read_config()
			return super(Config,self).get(self.section_name,item)
		except (cparser.NoOptionError,cparser.NoSectionError) as error:
			return None

	def set_values(self,item,value):
		try:
			super(Config,self).set(self.section_name,item,value)
		except cparser.NoSectionError:
			raise cparser.NoSectionError(self.section_name)

	def set_file_perm(self):
		os.chmod(self.file_path, 0o600)

	def auth(self):
		if (self.config_has_section() and self.get_val_from_config('token')):
			return True
		else:
			iocalls.print_text('\nError: You are not logged in. Please try this command after authentication--see "ax login"')
			return False

	def file_system_env(self):
		if (self.config_has_section() and not int(self.get_val_from_config('space')) and \
			not int(self.get_val_from_config('cloud'))):
			return True
		else:
			return False

	def space_env(self):
		if (self.config_has_section() and int(self.get_val_from_config('space')) and \
			not int(self.get_val_from_config('cloud'))):
			return True
		else:
			return False

	def cloud_env(self):
		if (self.config_has_section() and int(self.get_val_from_config('space')) and \
			(int(self.get_val_from_config('cloud')))):
			return True
		else:
			return False

	def write_to_config(self,item,value):
		if not self.config_has_section():
			self.add_section_to_config()
		self.set_values(item,value)

		with open(self.file_path,'w') as f:
			super(Config,self).write(f)

		self.set_file_perm()

	def initialize_config(self):
		self.write_to_config('username','')
		self.write_to_config('token','')
		self.write_to_config('dir','')
		self.write_to_config('id','')
		self.write_to_config('space','')
		self.write_to_config('spacename','')
		self.write_to_config('cloud','')
		self.write_to_config('cloud_id','')

	def update(self,username,token):
		self.write_to_config('username',username)
		self.write_to_config('token',token)
		self.write_to_config('dir','~antarin')
		self.write_to_config('space','0')
		self.write_to_config('cloud','0')


	def update_config_dir(self,message):
		message = json.loads(message)

		dir_name = message['current_directory']
		id_val = message['id']
		
		self.write_to_config('dir',dir_name)
		self.write_to_config('id',str(id_val))

	def update_config_space(self,message):

		spacename = message['spacename']
		self.write_to_config('space','1')
		self.write_to_config('spacename',spacename)

	def update_config_cloud(self,message):

		cloud_id = message['id']
		self.write_to_config('cloud','1')
		self.write_to_config('cloud_id',str(cloud_id))

	def quit_space(self):
		self.write_to_config('space','0')
		self.write_to_config('spacename','')
		self.write_to_config('cloud','0')
		self.write_to_config('cloud_id','')

	def quit_cloud(self):
		self.write_to_config('cloud','0')
		self.write_to_config('cloud_id','')


