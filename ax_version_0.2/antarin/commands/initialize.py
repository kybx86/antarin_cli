"""
	ax initialize <packagename> [<id>]
"""

from .base import Base
from ..utils import apicalls,iocalls

class Initialize(Base):

	def response_handler(self,payload):
		message = payload[1]['message']
		iocalls.print_text(message)

	def run(self):
		config = self.config
		self.endpoint = '/initialize/'

		if config.auth():
			if config.file_system_env():
				iocalls.print_not_valid_argument()
				self.system_exit()
			else:
				accesskey = None
				package = self.option_dict['<packagename>']
				if config.space_env(): 	
					if self.option_dict['--cloud']:
						if self.option_dict['--cloud'].isdigit():
							accesskey = self.option_dict['--cloud']
						else:
							iocalls.print_not_num_text()
							self.system_exit()
					else:
						iocalls.print_specify_accesskey()
						self.system_exit()
				payload = self.send_request(self.endpoint,None,accesskey,None,None,package)
				self.response_handler(payload)
			