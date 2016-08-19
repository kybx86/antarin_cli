"""
	Base class for all antarinX commands
"""

import os,sys
from ..config import Config
from ..utils import iocalls,apicalls
from ..__main__ import __doc__

commands = ['login','see','enter','delete','new','upload','add','exit','run','initialize','sleep','logout']

class Base(object):
	def __init__(self,option_dict,endpoint=None):
		"""
			Base class Constructor - sets values for the dictionary returned from docopt library function, the API
			endpoint value for the command, and also instantites the Config() class so that the config details are 
			available to all commands that inherit the Base class.
		"""
		self.option_dict = option_dict
		self.endpoint = endpoint
		self.config = Config()

	def run(self):
		"""
			Abstract run() method that needs to be implemented in all classes that inherit the Base class.
		"""
		raise NotImplementedError('An implementation of this method has to be provided.')

	def response_handler(self):
		raise NotImplementedError('An implementation of this method has to be provided.')


	def get_arguments(self):
		"""
			This method gives all arguments that are passed on with the entered command.
		"""
		arguments = []
		for key,value in self.option_dict.items():
			if value and key not in commands:
				arguments.append(key)
		return arguments

	def system_exit(self):
		"""
			This method performs a safe exit() by either doing a sys.exit() or os.exit() -- usually called during
			keyboard interrupt/ payload request exceptions
		"""
		print("\n")
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)

	def config_set(self):
		"""
			This method performs a check to determine if the config file is empty or if the config file has the token
			value set -- called from the Login module
		"""
		if (self.config.config_has_section() and not self.config.get_val_from_config('token')) or (not self.config.config_has_section()):
			return 1
		elif self.config.get_val_from_config('token'):
			iocalls.print_text('\nLogged in as: %s' %self.config.get_val_from_config('username'))
			iocalls.print_text('Session Token: %s' %self.config.get_val_from_config('token'))
			return 0
	
	def login(self):
		"""
			This method takes care of user authentication setup - fetches user input and makes an API request
		"""
		try:
			while True:
				userdata = iocalls.get_user_auth_details()
				payload = apicalls.api_send_request(self.endpoint,'POST',config_data=userdata)
				if payload[0]:
					token = payload[1]['key']
					self.config.update(userdata['username'],token)
					iocalls.print_text('\nantarinX login succesful!\n')
					iocalls.print_text('Logged in as: %s' %userdata['username'])
					iocalls.print_text('Session Token: %s' %token)
					break
				else:
					iocalls.print_text('Invalid username and/or password\n')
		except KeyboardInterrupt:
			self.system_exit()

	def get_env(self):
		if self.config.file_system_env():
			return 'filesystem'
		elif self.config.space_env():
			return 'space'
		elif self.config.cloud_env():
			return 'cloud'

	def display_env(self):
		value = self.get_env().strip()
		if value is 'filesystem':
			message = 'FILE SYSTEM'
		elif value is 'space':
			message = 'SPACE'
		elif value is 'cloud':
			message = 'CLOUD'
		iocalls.print_text(message)

	def display_help(self):
		help_text = __doc__
		iocalls.print_text(help_text)

	def send_request(self,api_endpoint,argument,argval=None):
		config_data = self.config.get_values()
		config_data['argument'] = argument
		config_data['env'] = self.get_env().strip()
		config_data['argval'] = argval

		payload  = apicalls.api_send_request(api_endpoint,'POST',config_data)
		return payload

