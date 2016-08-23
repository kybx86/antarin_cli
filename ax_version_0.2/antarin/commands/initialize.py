"""
	ax initialize <packagename> [<id>]
"""

from .base import Base
from ..utils import apicalls,iocalls

class Initialize(Base):

	def response_handler(self,payload):
		print(payload[1])

	def run(self):
		config = self.config
		self.endpoint = '/initialize/'

		if config.auth():
			if config.file_system_env():
				iocalls.print_not_valid_argument()
				self.system_exit()
			else:
				accesskey = None
				packagename = self.option_dict['<packagename>'] #returns a list
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
				payload = self.send_request(self.endpoint,None,accesskey,None,None,packagename)
				self.response_handler(payload)
			