"""
	logout command
"""

from .base import Base
from ..utils import apicalls,iocalls
from ..config import Config

class Logout(Base):

	def run(self):
		config = self.config
		self.endpoint = '/rest-logout/'

		if (config.config_has_section() and config.get_val_from_config('token')):
			connection = apicalls.api_send_request(self.endpoint,'POST',config_data=config.get_values())
			if connection[0]:
				config.initialize_config()
				iocalls.print_text("\n" + connection[1]['message'])
			elif not connection[0]:
				iocalls.print_text(connection[1])
		else:
			iocalls.print_text('\nError: You are not logged in. Please try this command after authentication--see "ax login"')