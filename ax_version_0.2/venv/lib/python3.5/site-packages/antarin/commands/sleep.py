"""
	ax sleep [<id>]
"""
from .base import Base
from ..utils import apicalls,iocalls

class Sleep(Base):

	def response_handler(self,payload):
		print(payload[1])

	def run(self):
		config = self.config
		self.endpoint = '/sleep/'

		if config.auth():
			if config.file_system_env():
				iocalls.print_not_valid_argument()
				self.system_exit()
			else:
				accesskey = None
				if config.space_env(): 	
					if self.option_dict['<id>']:
						if self.option_dict['<id>'].isdigit():
							accesskey = self.option_dict['<id>']
						else:
							iocalls.print_not_num_text()
							self.system_exit()
					else:
						iocalls.print_specify_accesskey()
						self.system_exit()
				payload = self.send_request(self.endpoint,None,accesskey)
				self.response_handler(payload)
			
