"""
	ax new (folder|space|cloud) <name>
"""
	
from .base import Base
from ..utils import apicalls,iocalls

class New(Base):

	def response_handler(self,payload,argument,value):
		message = payload[1]['message']
		if payload[0]:
			text = 'Created ' + argument
			if argument == 'folder':
				iocalls.print_text(text + ': ' + value)
			else:
				access_key = payload[1]['message']['access_key']
				iocalls.print_text(text + ': ' + value + ' with ID: '+ str(access_key))
		else:
			iocalls.print_text(message)

	def check_env_argument(self,argument):
		if (argument == 'folder' and self.config.file_system_env()) or \
			(argument == 'space' and self.config.file_system_env()) or \
			(argument == 'cloud' and self.config.space_env()):
			return True
		else:
			return False

	def run(self):
		config = self.config
		self.endpoint = '/new/'
		argument = self.get_arguments()[0]
		value = self.option_dict['<name>']
		
		if config.auth():			
			if New.check_env_argument(self,argument):
				if argument != 'cloud':
					payload = self.send_request(self.endpoint,argument,value)
					self.response_handler(payload,argument,value)
				else:
					try:
						cloud_data = iocalls.get_cloud_data()
					except KeyboardInterrupt:
						print('\n')
						self.system_exit()
					payload = self.send_request(self.endpoint,argument,value,cloud_data)
					self.response_handler(payload,argument,value)
			else:
				iocalls.print_not_valid_argument()


