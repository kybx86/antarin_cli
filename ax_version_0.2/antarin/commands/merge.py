"""
	ax merge <source_id> <destination_id>
"""

from .base import Base
from ..utils import apicalls,iocalls

class Merge(Base):

	def response_handler(self,payload):
		message = payload[1]['message']
		iocalls.print_text(message)
		
	def run(self):
		config = self.config
		self.endpoint = '/merge/'

		if config.auth():
			if self.config.space_env():
				source_id = self.option_dict['<source_id>']
				destination_id = self.option_dict['<destination_id>']
				if source_id.isdigit() and destination_id.isdigit():
					payload = self.send_request(self.endpoint,None,None,None,None,None,None,None,source_id,destination_id)
					self.response_handler(payload)
				else:
					iocalls.print_not_num_text()
			else:
				iocalls.print_not_valid_argument()