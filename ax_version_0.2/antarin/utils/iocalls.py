"""
	antarinX I/O methods
"""
# This file contains all input/ouput methods used in antarinX CLI

import os
import sys
import getpass
from . import _color as cl

def print_text(message):
	cl.out(cl.blue('\n' + message + '\n'))

def print_text_bold(message):
	print(cl.blue(cl.bold(message)))

def print_exception_error(message):
	print(cl.red(message))

def print_not_inside_space_message():
	message = 'Error: You are not inside a space environment. Please try this command after entering a space--see "ax enter <space>"'
	print_text('\n'+ message)

def print_not_inside_cloud_message():
	message = 'Error: You are not inside a cloud environment. Please try this command after entering a cloud--see "ax enter <cloud>"'
	print_text('\n'+ message)

def print_not_num_text():
	message = 'Error: Not a valid argument value. Accepted value is a 4 digit number.'
	print_text(message)

def print_not_valid_argument():
	message = 'This argument is not valid in the current anatrinX environment. Verify your current environment -- check "ax see env"'
	print_text(message)

def print_specify_accesskey():
	message = 'Error: Please specify accesskey of the cloud.'
	print_text(message)

def print_log(message):
	
	print_text_bold('\nProject log:\n')
	for item in message:
		cl.out(cl.blue('\t{0} {1}\n').format(item[0], item[1]))
		# the log could be formated a lot better. 

def print_file_list(message):
	cl.out(cl.blue(cl.bold('\nMy files:\n')))
	for item in range(len(message)):
		cl.out(cl.blue('\n\t' + message[item]))
	cl.out('\n')

def print_clouds(message, argument):
	cl.out(cl.blue(cl.bold("\nMy {0}:").format(argument)))
	print('\n')
	for item in range(len(message)):
		space_entry = message[item]
		space_entry = space_entry.split('\t')
		space_name = space_entry[0].split(':')[1]
		cl.out(cl.blue(cl.bold("\t{0} name:\t").format(argument.title())) + 
			cl.blue('{:12s}'.format(space_name[:12])))

def print_spaces(message, argument):
	cl.out(cl.blue(cl.bold("\nMy {0}:").format(argument)))
	print('\n')
	for item in range(len(message)):
		space_entry = message[item]
		space_entry = space_entry.split('\t')
		space_name = space_entry[0].split(':')[1]
		cl.out(cl.blue(cl.bold("\t{0} name:\t").format(argument.title())) + 
			cl.blue('{:12s}'.format(space_name[:12])))
		cl.out(cl.blue(cl.bold('\tPermissions:\t') + cl.blue(space_entry[1])))
		cl.out(cl.blue(cl.bold('\t{0} ID\t').format(argument.title()) + 
			cl.blue(space_entry[2])))
		cl.out('\n')

def print_summary(message,env):
	summary = message
	if env == 'space':
		space_name = summary['projectname'].split(':')[1]
		admin = summary['admin'].split('(')
		
		cl.out(cl.blue(cl.bold('\nSpace details:\n')))
		cl.out(cl.blue(cl.bold('\n\tSpace name: ')) + cl.blue(space_name))
		cl.out(cl.blue(cl.bold('\n\tAdmin: ') + cl.blue(admin[0].title()) + 
			cl.blue(' -> ') + cl.blue(admin[1][:-1])))
		#--iterating for fields of variable length
		cl.out(cl.blue(cl.bold('\n\tContributors: \n')))
		for item in range(len(summary['contributors'])):
			usr = summary['contributors'][item][0]
			usr_perms = summary['contributors'][item][1]
			cl.out(cl.blue("\n\t\t{0} \t{1}").format(usr.title(), usr_perms))
		print('\n')
		cl.out(cl.blue(cl.bold('\tProject files: \n')))
		for item in range(len(summary['file_list'])):
			filename = summmary['file_list'][item][0]
			owner = summmary['file_list'][item][1]
			cl.out(cl.blue("\n\t\t{0} \t{1}").format(owner.title(), filename))
		print('\n')
		cl.out(cl.blue(cl.bold('\tProject folders: \n')))
		for item in range(len(summary['folder_list'])):
			filename = summary['folder_list'][item][0]
			owner = summary['folder_list'][item][1].split('(')[0]
			cl.out(cl.blue("\n\t\t{0} \t{1}").format(owner.title(), filename))
		print('\n')

	if env == 'filesystem':
		cl.out(cl.blue(cl.bold('\nAccount\n')))
		cl.out(cl.blue(cl.bold('\n\tUser: ')) + 
			cl.blue('{0} {1}').format(summary['firstname'].title(), summary['lastname'].title()))
		cl.out(cl.blue(cl.bold('\n\tAntarin ID: ')) + cl.blue(summary['username']))
		cl.out(cl.blue(cl.bold('\n\tStorage Use: ')) + 
			cl.blue('{0} / {1}').format(summary['data_storage_used'], summary['data_storage_available']))
		# can add more to summary: 'status bar': spaces, clouds running, etc...
		print('\n')

def print_enter(message, arg):
	cl.out(cl.blue('\nEntered {0}: {1}\n').format(arg.title(), message['spacename'].split(':')[1]))



def get_user_auth_details():
	userdata = {}
	try:
		userdata['username'] = str(raw_input(cl.blue(cl.bold('Antarin ID: '))))
	except NameError:
		userdata['username'] = str(input(cl.blue(cl.bold('Antarin ID: '))))
	userdata['password'] = getpass.getpass(cl.blue(cl.bold('Password:(will be hidden as you type) ')))
	return userdata

def get_cloud_data():
	#TODO --> set default values when user entered value is empty
	cloud_data = {}
	try:
		cloud_data['ami_id'] = str(raw_input(cl.blue(cl.bold('Machine Image ID (AntarinX Linux AMI - ami-bd01cbdd): '))))
		cloud_data['instance_type'] = str(raw_input(cl.blue(cl.bold('Instance Type (t2.micro): '))))
		cloud_data['region'] = str(raw_input(cl.blue(cl.bold('Region (us-west-2):'))))
	except NameError:
		cloud_data['ami_id'] = str(input(cl.blue(cl.bold('Machine Image ID (AntarinX Linux AMI - ami-bd01cbdd): '))))
		cloud_data['instance_type'] = str(input(cl.blue(cl.bold('Instance Type (t2.micro): '))))
		cloud_data['region'] = str(input(cl.blue(cl.bold('Region (us-west-2):'))))
	return cloud_data

def get_user_choice():
	try:
		user_input = str(raw_input(cl.blue("\nAre you sure you want to delete this project and all the data associated with it? (yes/no) ")))
	except NameError:
		user_input = str(input(cl.blue("\nAre you sure you want to delete this project and all the data associated with it? (yes/no) ")))
	
	user_input = user_input.strip()
	if user_input.strip() == "yes":
		return True
	elif user_input == "no":
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
	else:
		print_text("Invalid response. Please type 'yes' or 'no'")

def get_password():
	pwd = getpass.getpass(cl.blue('Enter your antarinX password:(will be hidden as you type) '))
	return pwd

		
def get_user_choice_rename():
	try:
		user_input = str(raw_input(cl.blue("Do you want to rename the file? (yes/no): ")))
	except NameError:
		user_input = str(input(cl.blue("Do you want to rename the file? (yes/no): ")))

	user_input = user_input.strip()
	if user_input.strip() == "yes":
		return True
	elif user_input == "no":
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
	else:
		print_text("Invalid response. Please type 'yes' or 'no'")
		return False

def get_new_filename():
	try:
		new_filename = str(raw_input(cl.blue("Enter new file name with extension (cannot be empty): ")))
	except NameError:
	 	new_filename = str(input(cl.blue("Enter new file name with extension (cannot be empty): ")))
	new_filename = new_filename.strip()
	if new_filename != "" and new_filename != " ":
		return new_filename
	else:
		print_text("Invalid file name.")
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)




