"""
	Base class for all antarinX commands
"""
from ..config import Config

class Base(object):
	def __init__(self,option_dict,endpoint=None):
		self.option_dict = option_dict
		self.endpoint = endpoint
		self.config = Config()
		
	def run(self):
		raise NotImplementedError('An implementation of this method has to be provided.')

