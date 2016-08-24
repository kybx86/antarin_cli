"""
	ax delete ((space|cloud) <id> | -i <item>)
"""

from .base import Base
from ..utils import apicalls,iocalls

class Delete(Base):

	def response_handler(self, payload):
		message = payload[1]['message']
		iocalls.print_text(message)

	def check_env_argument(self,argument):
		if (argument == '-i') or (argument == 'space' and self.config.file_system_env()) or \
			(argument == 'cloud' and self.config.space_env()):
			return True
		else:
			return False

	def run(self):
		config = self.config
		self.endpoint = '/delete/'

		if config.auth():
			argument = self.get_arguments()[0]
			if Delete.check_env_argument(self,argument):
				if argument == '-i':
					value = self.option_dict['<item>']
				
				if argument == 'space' or argument == 'cloud':
					value = self.option_dict['<id>']
					if not value.isdigit():
						iocalls.print_not_num_text()
						self.system_exit()
				
				if argument == 'space':
					self.delete_space(self.endpoint, argument, value)
				
				payload = self.send_request(self.endpoint, argument, value)
				self.response_handler(payload)
			else:
				iocalls.print_not_valid_argument()
