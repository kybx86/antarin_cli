"""
	ax enter ((folder) <name> | (space|cloud) <id>)
"""

from .base import Base
from ..utils import apicalls,iocalls

class Enter(Base):

	def response_handler(self,payload):
		pass

	def run(self):
		config = self.config
		self.endpoint = '/enter/'
		argument = self.get_arguments()[0]
		
		if config.auth():
			argument = argument.strip()
			if argument == 'folder':
				value = self.option_dict['<name>']
			elif argument == 'space': 
				value = self.option_dict['<id>']

			payload = self.send_request(self.api_endpoint,argument,value)