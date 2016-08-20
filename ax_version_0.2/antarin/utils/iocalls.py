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
	message = 'This argument is not valid in the current anatrinX environment. Verify your current environment -- check "ax see <env>"'
	print_text(message)

def print_log(message):
	pass
	# print_text_bold('\nProject log:\n')
	# for item in message:
	# 	print_text('\t%s %s' %(item[0], item[1]))

def print_file_list(message):
	pass

def print_spaces_clouds(message):
	pass

def print_summary(message,env):
	pass
	# if env == 'space':
	# 	summary_file = message
	# 	project_name = summary_file['projectname'].split(':')[1]

	# 	print_text_bold('\nProject Details:\n')
	# 	print_text_bold('\n\tProject Name: ') + print_text(project_name)
	# 	print_text_bold('\n\tAdmin: ') + print_text(summary_file['admin'])
		
	# 	#--iterating for fields that can contain variable length fields
	# 	print_text_bold('\n\tContributors: \n')
	# 	for i in xrange(len(summary_file['contributors'])):
	# 		username = summary_file['contributors'][i][0]
	# 		user_status = summary_file['contributors'][i][1]
	# 		print_text("\t\t%s \t%s" %(username, user_status))

	# 	out(ax_blue(bold('\tProject Files: \n')))
	# 	for i in xrange(len(summary_file['file_list'])):
	# 		filename = summary_file['file_list'][i][0]
	# 		owner = summary_file['file_list'][i][1]
	# 		print_text("\t\t%s \t%s" %(owner, filename))
		
	# 	out(ax_blue(bold('\tProject Folders: \n')))
	# 	for i in xrange(len(summary_file['folder_list'])):
	# 		foldername = summary_file['folder_list'][i][0]
	# 		owner = summary_file['folder_list'][i][1]
	# 		print_text("\t\t%s \t%s" %(owner, foldername))

	# if env == 'filesystem':
	# 	summary_file = message     
	# 	print_text_bold('\nAccount:\n')
	# 	print_text_bold('\n\tUser: ')
	# 	cl.ax_blue(summary_file['firstname']+' ') + cl.ax_blue(summary_file['lastname'])
	# 	print_text_bold('\n\tAntarin ID: ')
	# 	cl.ax_blue(summary_file['username'])
	# 	print_text_bold('\n\tStorage Use: ')
	# 	cl.ax_blue('%s / %s' %(summary_file['data_storage_used'], summary_file['data_storage_available']))
	# 	print('\n')

def get_user_auth_details():
	userdata = {}
	try:
		userdata['username'] = str(raw_input(cl.ax_blue(cl.bold('Antarin ID: '))))
	except NameError:
		userdata['username'] = str(input(cl.ax_blue(cl.bold('Antarin ID: '))))
	userdata['password'] = getpass.getpass(cl.ax_blue(cl.bold('Password:(will be hidden as you type) ')))
	return userdata

def get_cloud_data():
	#TODO --> set default values when user entered value is empty
	cloud_data = {}
	try:
		cloud_data['ami_id'] = str(raw_input(cl.ax_blue(cl.bold('Machine Image ID (AntarinX Linux AMI - ami-bd01cbdd): '))))
		cloud_data['instance_type'] = str(raw_input(cl.ax_blue(cl.bold('Instance Type (t2.micro): '))))
		cloud_data['region'] = str(raw_input(cl.ax_blue(cl.bold('Region (us-west-2):'))))
	except NameError:
		cloud_data['ami_id'] = str(input(cl.ax_blue(cl.bold('Machine Image ID (AntarinX Linux AMI - ami-bd01cbdd): '))))
		cloud_data['instance_type'] = str(input(cl.ax_blue(cl.bold('Instance Type (t2.micro): '))))
		cloud_data['region'] = str(input(cl.ax_blue(cl.bold('Region (us-west-2):'))))
	return cloud_data


