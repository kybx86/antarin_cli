"""
	ax exit [space|cloud]
"""

from .base import Base
from ..utils import apicalls,iocalls

class Exit(Base):

	def run(self):
		config = self.config

		if config.auth():
			argument = self.get_arguments()
			if argument:
				argument = argument[0]
			
			if not self.config.file_system_env():
				if (not argument) or (argument == 'space') or (argument == 'cloud' and self.config.cloud_env()):
					self.quit_env(argument)
					self.system_exit()
			
			iocalls.print_not_valid_argument()
