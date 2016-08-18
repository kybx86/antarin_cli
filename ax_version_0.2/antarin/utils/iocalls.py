"""
	antarinX I/O methods
"""
# This file contains all input/ouput methods used in antarinX CLI

import os
import sys
import getpass
from . import _color as cl

def print_text(message):
	print(cl.ax_blue(message))

def print_text_bold(message):
	print(cl.ax_blue(cl.bold(message)))

def print_exception_error(message):
	print(cl.ax_red(message))
	
def get_user_auth_details():
	userdata = {}
	try:
		userdata['username'] = str(raw_input(cl.ax_blue(cl.bold('Antarin ID: '))))
	except NameError:
		userdata['username'] = str(input(cl.ax_blue(cl.bold('Antarin ID: '))))
	userdata['password'] = getpass.getpass(cl.ax_blue(cl.bold('Password:(will be hidden as you type) ')))
	return userdata

