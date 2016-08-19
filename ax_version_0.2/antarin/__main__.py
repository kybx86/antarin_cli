"""
antarinX CLI main script

Usage:
	ax login
	ax see (files|spaces|clouds|path|env|summary|log|help)
	ax enter ((folder) <name> | (space|cloud) <id>)
	ax delete ([space|cloud] <id> | <item>)
	ax new <folder|space|cloud> <name>
	ax upload <item>
	ax add ([--env|--data|--code] <packagename> <item> | <item> | contributor <username>)
	ax exit [space|cloud]
	ax run <shell_command> <package_name>
	ax initialize [<id>]
	ax sleep [<id>]
	ax logout

"""

import docopt 
import inspect 
from . import __version__ as VERSION
from . import commands
from . import utils

def main():
	option_dict = docopt.docopt(__doc__,version=VERSION)
	#for key,value in option_dict.iteritems(): -- python2.7 -> use try-catch
	for key,value in option_dict.items():
		if hasattr(commands,key) and value:
			module = getattr(commands,key)
			commands_list = inspect.getmembers(module, inspect.isclass)
			command = [command[1] for command in commands_list if command[0] != 'Base' and command[0]!= 'Config'][0]
			command = command(option_dict)
			command.run()

if __name__ == "__main__":
    main()