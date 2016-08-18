"""
login command
"""

import sys
import os
from .base import Base
from ..utils import apicalls,iocalls

class Login(Base):

	def run(self):
		config = self.config
		self.endpoint = '/rest-auth/login/'
		
		if (config.config_has_section() and not config.get_val_from_config('token')) or (not config.config_has_section()):
			config.initialize_config()
			iocalls.print_text('\nEnter your antarinX credentials\n')
			try:
				while True:
					userdata = iocalls.get_user_auth_details()
					connection = apicalls.api_send_request(self.endpoint,'POST',config_data=userdata)
					if connection[0]:
						token = connection[1]['key']
						config.update(userdata['username'],token)
						iocalls.print_text('\nantarinX login succesful!\n')
						iocalls.print_text('Logged in as: %s' %userdata['username'])
						iocalls.print_text('Session Token: %s' %token)
						break
					else:
						iocalls.print_text('Invalid username and/or password\n')
			except KeyboardInterrupt:
				print("\n")
				try:
					sys.exit(0)
				except SystemExit:
					os._exit(0)
		
		elif config.get_val_from_config('token'):
			iocalls.print_text('\nLogged in as: %s' %config.get_val_from_config('username'))
			iocalls.print_text('Session Token: %s' %config.get_val_from_config('token'))
