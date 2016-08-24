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
				text = 'Added ' + value + ' to this space.'
			elif argument[0:2] == '--':
				if value:
					text = 'Added ' + value + ' to this cloud.'
				else:
					text = 'Added package to this cloud.'
			iocalls.print_text(text)
		else:
			iocalls.print_text(message['message'])

	def check_env_argument(self,argument):
		if (argument=='-i' and self.config.space_env()) or \
		(argument=='contributor' and self.config.space_env()) or\
		(argument[0:2] == '--' and self.config.cloud_env()):
			return True
		else:
			return False

	def run(self):
		config = self.config
		self.endpoint = '/add/'

		if config.auth():
			argument = self.get_arguments()[0]
			if not self.config.file_system_env() and Add.check_env_argument(self,argument):
				if argument == 'contributor' or argument == '-i':
					if argument == 'contributor':
						value = self.option_dict['<username>']
					if argument == '-i':
						value = self.option_dict['<item>']
					payload = self.send_request(self.endpoint,argument,value)
					self.response_handler(payload,argument,value)
				
				if argument[0:2] == '--':
					packagename =  self.option_dict['<packagename>']
					value = None
					if '<item>' in self.option_dict:
						value = self.option_dict['<item>']
					payload = self.send_request(self.endpoint,argument,value,None,None,packagename)
					self.response_handler(payload,argument,value)
			else:
				iocalls.print_not_valid_argument()