from ConfigParser import SafeConfigParser

def write(item,value):
	config = SafeConfigParser()
	config.read('config.ini')
	if not config.has_section('user_details'):
		config.add_section('user_details')
	config.set('user_details', item, value)

	with open('config.ini', 'w') as f:
	    config.write(f)