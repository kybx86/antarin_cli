from . import Base
from ConfigParser import SafeConfigParser

class Logout(Base):

	def run(self):
		config = SafeConfigParser()
		config.read('config.ini')
		config.set('user_details', 'username', "")
		config.set('user_details','token', "")

		with open('config.ini', 'w') as f:
		    config.write(f)