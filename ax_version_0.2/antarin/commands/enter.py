"""
	ax enter ((folder) <name> | (space|cloud) <id>)
"""

from .base import Base
from ..utils import apicalls,iocalls

class Enter(Base):

	def response_handler(self,payload,argument):

		message = payload[1]['message']
		if payload[0]:
			if argument == 'folder':
				self.config.update_config_dir(message)
			if argument == 'space':
				self.config.update_config_space(message)
				#iocalls.print_enter(message, argument)
			if argument == 'cloud':
				self.config.update_config_cloud(message)
				print(message['name'])
				#iocalls.print_enter(message, argument)
		else:
			iocalls.print_text(message)

	def run(self):
		config = self.config
		self.endpoint = '/enter/'
		argument = self.get_arguments()[0]
		
		if config.auth():
			argument = argument.strip()
			
			if argument == 'folder':
				if self.config.file_system_env():
					value = self.option_dict['<name>']
				else:
					iocalls.print_not_valid_argument()
					self.system_exit()

			else:
				if (argument == 'space' and self.config.file_system_env()) or (argument == 'cloud' and self.config.space_env()): 
					value = self.option_dict['<id>'].strip()
					if not value.isdigit():
						iocalls.print_not_num_text()
						self.system_exit()
				else:
					iocalls.print_not_valid_argument()
					self.system_exit()
			
			payload = self.send_request(self.endpoint,argument,value)
			self.response_handler(payload,argument)