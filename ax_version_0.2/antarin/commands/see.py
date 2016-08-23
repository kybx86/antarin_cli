"""
	ax see (files|spaces|clouds|path|env|summary|log|help)
"""

from .base import Base
from ..utils import apicalls,iocalls

class See(Base):

	def response_handler(self, payload, argument):
		#print(payload[1]['message'])
		message = payload[1]['message']
		if payload[0]:
			env = self.get_env()
			if argument == 'log':
				iocalls.print_log(message)
			if argument == 'summary':
				iocalls.print_summary(message, env)
			if argument == 'files':
				iocalls.print_file_list(message)
			if argument == 'spaces':
				iocalls.print_spaces(message, argument)
			if argument == 'clouds':
				iocalls.print_clouds(message, argument)
			if argument == 'path':
				message = message.strip('"')
				iocalls.print_text(message)
		else:
			iocalls.print_text(message)

	def check_env_argument(self, argument):
		if (argument == 'files' or argument == 'summary') or \
			((argument == 'log'or argument == 'clouds') and self.config.space_env()) or \
			((argument == 'path' or argument == 'spaces') and self.config.file_system_env()):
			return True
		else:
			return False

	def run(self):
		config = self.config
		self.endpoint = '/see/'
		argument = self.get_arguments()[0]
		
		if config.auth():
			argument = argument.strip()
			if argument == 'env':
				self.display_env()
			elif argument == 'help':
				self.display_help()
			else:
			 	if See.check_env_argument(self,argument):
			 		payload = self.send_request(self.endpoint,argument)
			 		self.response_handler(payload,argument)
			 	else:
			 		iocalls.print_not_valid_argument()
			 		