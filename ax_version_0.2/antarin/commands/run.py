"""
	ax run <shell_command> <package_name> [<id>]
"""
from .base import Base
from ..utils import apicalls,iocalls

class Run(Base):

	def response_handler(self,payload):
		message = payload[1]['message']
		iocalls.print_run_output(message)

	def run(self):
		config = self.config
		self.endpoint = '/run/'

		if config.auth():
			if config.file_system_env():
				iocalls.print_not_valid_argument()
				self.system_exit()
			else:
				accesskey = None
				packagename = self.option_dict['<packagename>']
				shell_command = self.option_dict['<shell_command>']
				if not shell_command.startswith('python'):
					iocalls.print_not_valid_shell_command()
					self.system_exit()

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
				
				payload = self.send_request(self.endpoint,None,accesskey,None,None,packagename,shell_command)
				self.response_handler(payload)