"""
	logout command
"""

from .base import Base
from ..utils import apicalls,iocalls
from ..config import Config

class Logout(Base):

	def response_handler(self,payload):
		message = payload[1]['message']
		if payload[0]:
			self.config.initialize_config()
			iocalls.print_text("\n" + message)
		elif not payload[0]:
			iocalls.print_text(message)

	def run(self):
		config = self.config
		self.endpoint = '/rest-logout/'

		if config.auth():
			payload = apicalls.api_send_request(self.endpoint,'POST',config_data=config.get_values())
			self.response_handler(payload)
			