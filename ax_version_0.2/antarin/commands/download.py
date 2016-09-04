"""
	ax download <filename>
"""


from .base import Base
from ..utils import apicalls,iocalls

class Download(Base):
	def response_handler(self, payload):
		message = payload[1]['message']
		iocalls.print_text(message)

	def run(self):
		config = self.config
		self.endpoint = '/download/'

		if config.auth():
			filename = self.option_dict['<filename>']
			payload = self.send_request(self.endpoint, None, filename)
			self.response_handler(payload)
			