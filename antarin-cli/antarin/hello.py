class Hello(object):
 	"""docstring for Hello"""
	def __init__(self, message):
 		self.message= message

 	def display_message(self):
 		 print 'Hello, ' + self.message + '!'
 		