"""
login command
"""

from .base import Base
from ..utils import apicalls,iocalls

class Login(Base):

	def run(self):
		config = self.config
		self.endpoint = '/rest-auth/login/'
		
		if self.config_set():
			config.initialize_config()
			iocalls.print_text('\nEnter your antarinX credentials\n')
			self.login()
		
	def response_handler(self):
		pass
