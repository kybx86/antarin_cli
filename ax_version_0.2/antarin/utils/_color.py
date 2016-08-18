## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##

import sys
from termcolor import colored 

# This file uses the termcolor lib to output colored text in terminal. 
# Usage: colors.py should be imported wherever text needs to be printed to terminal--doing
# I created the function 'ax_blue' to simplify the usage of this lib. 
#
# example.py:
#
#		from colors import ax_blue
#
#		name = 'kevin' 
#		print ax_blue('Hello %s' %(name))


ax_blue = lambda x: colored(x, 'cyan')

ax_red = lambda x:colored(x,'red')

bold    = lambda x: ('\033[1m' + x + '\033[0m')

out     = lambda x: sys.stdout.write(x)

