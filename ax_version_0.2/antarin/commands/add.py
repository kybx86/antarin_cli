"""
	ax add (--env <packagename> |(--data|--code) <packagename> <item> | -i <item> | contributor <username>)
"""


from .base import Base
from ..utils import apicalls,iocalls

class Add(Base):

	def response_handler(self,payload,argument,value):
		message = payload[1]['message']
		if payload[0]:
			if argument == 'contributor':
				text = 'Added ' + value + ' as contributor to this space.'
			elif argument == '-i':
				text = 'Added ' + value 
			iocalls.print_text(text)
		else:
			iocalls.print_text(message['message'])

	def check_env_argument(self,argument):
		if (argument=='-i' and (self.config.space_env() or self.config.cloud_env())) or \
		(argument=='contributor' and self.config.space_env()):
			return True
		else:
			return False

	def run(self):
		config = self.config
		self.endpoint = '/add/'

		if config.auth():
			argument = self.get_arguments()[0]
			if not self.config.file_system_env() and Add.check_env_argument(self,argument):
				if argument == 'contributor':
					value = self.option_dict['<username>']
					payload = self.send_request(self.endpoint,argument,value)
					self.response_handler(payload,argument,value)
				
				if argument == '-i':
					value = self.option_dict['<item>']
					if value.startswith('~antarin') or value.startswith('~space'):
						payload = self.send_request(self.endpoint,argument,value)
						self.response_handler(payload,argument,value)
					else:
						iocalls.print_not_absolute_path()
			else:
				iocalls.print_not_valid_argument()