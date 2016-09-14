"""
	antarinX I/O methods
"""
# This file contains all input/ouput methods used in antarinX CLI
from __future__ import print_function

import os
import sys
import getpass

from . import _color as cl
from . import utilities as ut

def print_text(message, newline=None):

	cl.out(cl.blue("\n{}".format(message)))
	cl.out('\n')

def print_text_bold(message):
	print(cl.blue(cl.bold(message)))

def print_exception_error(message):
	print(cl.red(message)) #red

def print_not_inside_space_message():
	message = 'Error: You are not inside a space environment. Please try this command after entering a space--see "ax enter <space>"'
	cl.out(cl.blue("\n{}".format(message)))
	cl.out('\n')

def print_not_inside_cloud_message():
	message = 'Error: You are not inside a cloud environment. Please try this command after entering a cloud--see "ax enter <cloud>"'
	cl.out(cl.blue("\n{}".format(message)))
	cl.out('\n')

def print_not_absolute_path():
	message = 'Error: Please provide the absolute path of file/folder/package.'
	cl.out(cl.blue("\n{}".format(message)))
	cl.out('\n')

def print_not_num_text():
	message = 'Error: Not a valid argument value. Accepted value is a 3 digit ID number' 
	cl.out(cl.blue("\n{}".format(message)))
	cl.out('\n')

def print_not_valid_argument():
	message = "Error: This argument is not valid in the current anatrinX environment. Verify your current environment -- check 'ax see env'"
	cl.out(cl.blue("\n{}".format(message)))
	cl.out('\n')

def print_specify_accesskey():
	message = 'Error: Please specify accesskey of the cloud.'
	cl.out(cl.blue("\n{}".format(message)))
	cl.out('\n')

def print_not_valid_shell_command():
	message = 'Error: Not a valid shell command. Please make sure its in the format "python <file_path>"'
	cl.out(cl.blue("\n{}".format(message)))
	cl.out('\n')

def print_run_output(message):
	if type(message) is list:
		for item in message:
			print_text(item)
	else:
		print_text(message)

def print_monitor_text(message):

	cl.out(cl.blue(cl.bold('\nActivity monitor:\n'))) 
	cl.out('\n')

	message = sorted(message)
	sizes = ut.check_name_size(message, dtype='monitor')
	for item in message:
		cloudname = item[0]
		# space_owner = item[1].split(':')[0]
		cloud_owner= item[3]
		space_name = item[1].split(':')[1]
		status = item[2]
		cl.out(cl.blue(cl.bold("\tSpace: ") + cl.blue("{0:{1}s}".format(space_name[:sizes['space_size']], sizes['space_size']))))
		cl.out(cl.blue(cl.bold("  | Cloud: ") 
			+ cl.blue("{0:{1}s}".format(cloudname[:sizes['cloud_size']], sizes['cloud_size']))))
		cl.out(cl.blue(cl.bold("  | Owner: ") 
			+ cl.blue("{0:{1}}".format(cloud_owner[:sizes['owner_size']], sizes['owner_size']))))
		cl.out(cl.blue(cl.bold("  | State: ") 
			+ cl.blue("{0:{1}s}".format(status, 15))))
		cl.out('\n')

def print_clone(message):
	cl.out(cl.blue("\nCloned with cloud ID: {0}\n".format(message)))

def print_download(message):
	cl.out(cl.blue("\nFile for download available at:\n{0}\n".format(message)))
		
def print_login(message, token):

	cl.out(cl.blue('\nantarinX login succesful!'))
	cl.out(cl.blue('\nLogged in as: {0}').format(message))
	cl.out(cl.blue('\nSession token: {0}').format(token))
	cl.out('\n')

def print_log(message):
	
	print_text_bold('\nSpace log:\n') 
	for item in message:
		time = ut.utc_to_local(item[0])
		cl.out(cl.blue('\t{0}'.format(time)) + cl.blue(cl.bold(' -> ')) + cl.blue('{0}\n').format(item[1]))
		# the log could be formated a lot better. 

def print_file_list(message):
	
	cl.out(cl.blue(cl.bold('\nFiles:\n')))
	for item in range(len(message)):
		cl.out(cl.blue('\n\t' + message[item]))
	cl.out('\n')

def print_clouds(message, argument):
	cl.out(cl.blue(cl.bold("\n{0}:").format(argument.title())))
	print('\n')	
	size = ut.check_name_size(message, dtype='cloud')
	for item in range(len(message)):
		cloud_entry = message[item]
		cloud_entry = cloud_entry.split('\t')
		cloud_name = cloud_entry[0]
		cl.out(cl.blue(cl.bold("\t{0} name: ").format(argument.title()[:-1])) + 
			cl.blue('{0:{1}s}'.format(cloud_name[:size], size)))
		cl.out(cl.blue(cl.bold('\t| Owner: ') + cl.blue(cloud_entry[1])))
		cl.out(cl.blue(cl.bold('\t| {0} ID: ').format(argument.title()[:-1]) + 
			cl.blue(cloud_entry[2])))
		cl.out('\n')

def print_spaces(message, argument):
	cl.out(cl.blue(cl.bold("\nMy {0}:").format(argument)))
	print('\n')
	size = ut.check_name_size(message, dtype='space')
	for item in range(len(message)):
		space_entry = message[item]
		space_entry = space_entry.split('\t')
		space_name = space_entry[0].split(':')[1]
		cl.out(cl.blue(cl.bold("\t{0} name: ").format(argument.title()[:-1])) + 
			cl.blue("{0:{1}s}".format(space_name[:size], size)))
		cl.out(cl.blue(cl.bold('\t| Permissions: ') + cl.blue(space_entry[1])))
		cl.out(cl.blue(cl.bold('\t| {0} ID: ').format(argument.title()[:-1]) + 
			cl.blue(space_entry[2])))
		cl.out('\n')

def print_summary(message,env):
	summary = message

	if env == 'filesystem':
		cl.out(cl.blue(cl.bold('\nAccount:\n')))
		cl.out(cl.blue(cl.bold('\n\tUser: ')) + 
			cl.blue('{0} {1}').format(summary['firstname'].title(), summary['lastname'].title()))
		cl.out(cl.blue(cl.bold('\n\tAntarin ID: ')) + cl.blue(summary['username']))
		cl.out(cl.blue(cl.bold('\n\tStorage Use: ')) + 
			cl.blue('{0} / {1}').format(summary['data_storage_used'], summary['data_storage_available']))
		# can add more to summary: 'status bar': spaces, clouds running, etc...
		print('\n')

	elif env == 'space':
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
			cl.out(cl.blue("\n\t\t{0} - {1}").format(usr.title(), usr_perms))
		print('\n')
		cl.out(cl.blue(cl.bold('\tSpace files: \n')))
		for item in range(len(summary['file_list'])):
			filename = summary['file_list'][item][0]
			owner = summary['file_list'][item][1].split('(')[0]
			cl.out(cl.blue("\n\t\t{0} |\t{1}").format(owner.title(), filename))
		print('\n')
		cl.out(cl.blue(cl.bold('\tSpace folders: \n')))
		for item in range(len(summary['folder_list'])):
			filename = summary['folder_list'][item][0]
			owner = summary['folder_list'][item][1].split('(')[0]
			cl.out(cl.blue("\n\t\t{0} |\t{1}").format(owner.title(), filename))
		print('\n')

	elif env == 'cloud':

		if message['instance_type'] == 't2.micro':
			instance_type = 'CPU = 1  | Mem = 1.00 GiB'
		elif message['instance_type'] == 'c4.large':
			instance_type = 'CPU = 2  | Mem = 3.75 GiB'
		elif message['instance_type'] == 'c4.xlarge':
			instance_type = 'CPU = 4  | Mem = 7.50 GiB'
		elif message['instance_type'] == 'c4.2xlarge':
			instance_type = 'CPU = 8  | Mem = 15.00 GiB'
		elif message['instance_type'] == 'c4.8xlarge':
			instance_type = 'CPU = 36 | Mem = 60.00 GiB'

		cl.out(cl.blue(cl.bold('\nCloud details:\n')))
		cl.out(cl.blue(cl.bold("\n\tOwner: ")) + cl.blue("{0}".format(message['username'])))
		cl.out(cl.blue(cl.bold("\n\tCloud name: ")) + cl.blue("{0}".format(message['cloudname'])))
		cl.out(cl.blue(cl.bold("\n\tMachine image: ")) + cl.blue("{0} ({1})".format('AntarinX Linux AMI', message['ami'])))
		cl.out(cl.blue(cl.bold("\n\tInstance type: ")) + cl.blue("{0}".format(instance_type)))
		cl.out(cl.blue(cl.bold("\n\tRegion: ")) + cl.blue("{0}".format(message['region'])))
		cl.out('\n')

def print_enter(message, arg):
	if arg == 'space':
		cl.out(cl.blue('\nEntered {0}: {1}\n').format(arg.title(), message['name'].split(':')[1]))
	elif arg == 'cloud':
		cl.out(cl.blue('\nEntered {0}: {1}\n').format(arg.title(), message['name']))

def get_user_auth_details():
	userdata = {}
	try:
		userdata['username'] = str(raw_input(cl.blue(cl.bold('Antarin ID: '))))
	except NameError:
		userdata['username'] = str(input(cl.blue(cl.bold('Antarin ID: '))))
	userdata['password'] = getpass.getpass(cl.blue(cl.bold('Password:(will be hidden as you type) ')))
	return userdata

def get_ami_val():
	l = ['1']
	try:
		cl.out(cl.blue(cl.bold('\nMachine image: ')))
		cl.out(cl.blue('\n\t 1.  AntarinX Linux AMI'))
		val = str(raw_input(cl.blue(cl.bold('\nEnter the option number: '))))
	except NameError:
		val = str(input(cl.blue(cl.bold('\nEnter the option number: '))))

	if not val.isdigit() or val not in l:
		print_text("Invalid response.")
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
	if val == '1':
		ami_id = 'ami-bd01cbdd'

	return ami_id

def get_instance_type_val():
	l = ['1','2','3', '4', '5']
	try:
		cl.out(cl.blue(cl.bold('\nInstance type: ')))
		cl.out(cl.blue('\n\t 1.  CPU = 1  | Mem = 1.00 GiB')) 	#t2.micro
		cl.out(cl.blue('\n\t 2.  CPU = 2  | Mem = 3.75 GiB')) 	#c4.large
		cl.out(cl.blue('\n\t 3.  CPU = 4  | Mem = 7.50 GiB')) 	#c4.xlarge
		cl.out(cl.blue('\n\t 4.  CPU = 8  | Mem = 15.00 GiB')) 	#c4.2xlarge
		cl.out(cl.blue('\n\t 5.  CPU = 36 | Mem = 60.00 GiB')) 	#c4.8xlarge 
		val = str(raw_input(cl.blue(cl.bold('\nEnter the option number: '))))
	except NameError:
		val = str(input(cl.blue(cl.bold('\nEnter the option number: '))))

	if not val.isdigit() or val not in l:
		print_text("Invalid response.")
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
	if val == '1':
		instance_type = 't2.micro'
	elif val == '2':
		instance_type = 'c4.large'
	elif val == '3':
		instance_type = 'c4.xlarge'
	elif val == '4':
		instance_type = 'c4.2xlarge'
	elif val == '5':
		instance_type = 'c4.8xlarge'

	return instance_type

def get_region_val():
	l = ['1']
	try:
		cl.out(cl.blue(cl.bold('\nRegion: ')))
		cl.out(cl.blue('\n\t 1.  us-west-2'))
		val = str(raw_input(cl.blue(cl.bold('\nEnter the option number: '))))
	except NameError:
		val = str(input(cl.blue(cl.bold('\nEnter the option number: '))))

	if not val.isdigit() or val not in l:
		print_text("Invalid response.")
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
	if val == '1':
		region = 'us-west-2' #make sure this is being set correctly. (yes. value is correct)
	return region

def get_cloud_data():
	cloud_data = {}
	cloud_data['ami_id'] = get_ami_val()
	cloud_data['instance_type'] = get_instance_type_val()
	cloud_data['region'] = get_region_val()
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




