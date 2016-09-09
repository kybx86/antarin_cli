"""
	ax monitor 
"""

from .base import Base
from ..utils import apicalls,iocalls

class Monitor(Base):
	def response_handler(self, payload):
		message = payload[1]['message']
		iocalls.print_monitor_text(message)

	def run(self):
		config = self.config
		self.endpoint = '/monitor/'

		if config.auth():
			payload = self.send_request(self.endpoint)
			self.response_handler(payload)
