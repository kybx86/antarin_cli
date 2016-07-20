## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from ConfigParser import SafeConfigParser
from os.path import expanduser

def write(item,value):
	config = SafeConfigParser()
	home_path = expanduser("~")
	filepath = home_path + '/.antarin_config.ini'
	config.read(filepath)
	if not config.has_section('user_details'):
		config.add_section('user_details')
	config.set('user_details', item, value)

	with open(filepath, 'w') as f:
	    config.write(f)