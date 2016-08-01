## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
import os
from _color import ax_blue

class Summary(Base):

	def run(self):

		#file should really be at: /usr/local/lib/python2.7/site-packages/antarin
		#OR the text file can be written to that path upon pip install

		dir_path  = '/usr/local/lib/python2.7/site-packages/antarin-1.0.0.dist-info'
		file_name = 'usage.txt'
		path = os.path.join(dir_path, file_name)
		os.system('more %s' %path) # only output that doesnt print blue... need to figure out

		# with open(path, 'r') as file:
		# 	file = file.readlines()
		# 	for i in xrange(0, len(file), 20):
		# 		print file[i:i+20]
		# 		raw_input("Press enter to see more")




	