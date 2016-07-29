## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
import os

class Summary(Base):

	def run(self):

		#file should really be at: /usr/local/lib/python2.7/site-packages/antarin
		#OR the text file can be written to that path upon pip install

		dir_path  = '/usr/local/lib/python2.7/site-packages/antarin-1.0.0.dist-info'
		file_name = 'usage.txt'
		path = os.path.join(dir_path, file_name)
		os.system('more %s' %path)




	