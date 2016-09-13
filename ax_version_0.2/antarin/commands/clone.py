"""
	ax clone <id>
"""

from .base import Base
from ..utils import apicalls,iocalls


class Clone(Base):

	def response_handler(self,payload):
		message = payload[1]['message']
		iocalls.print_clone(message)

	def run(self):
		config = self.config
		self.endpoint = '/clone/'

		if config.auth():
			if self.config.space_env():
				accesskey = self.option_dict['<id>']
				if accesskey.isdigit():
					payload = self.send_request(self.endpoint,None,accesskey)
					self.response_handler(payload)
				else:
					iocalls.print_not_num_text()
			else:
				iocalls.print_not_valid_argument()