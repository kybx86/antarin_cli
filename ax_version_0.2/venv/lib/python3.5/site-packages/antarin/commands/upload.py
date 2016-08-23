"""
	ax upload <item>
"""

import os
from .base import Base
from ..utils import apicalls,iocalls

class Upload(Base):

	def run(self):
		config = self.config
		self.endpoint = '/upload/'

		if config.auth():
			if self.config.file_system_env():
				filename = self.option_dict['<item>']
				if not os.path.isdir(filename):
					self.file_upload(self.endpoint,filename)
				else:
					self.folder_upload(self.endpoint,filename)
			else:
				iocalls.print_not_valid_argument()