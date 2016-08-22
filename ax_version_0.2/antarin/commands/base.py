"""
	Base class for all antarinX commands
"""

import os,sys,json
from ..config import Config
from ..utils import iocalls,apicalls
from ..__main__ import __doc__

commands = ['login','see','enter','delete','new','upload','add','exit','run','initialize','sleep','logout']

class Base(object):
	def __init__(self,option_dict,endpoint=None):
		"""
			Base class Constructor - sets values for the dictionary returned from docopt library function, the API
			endpoint value for the command, and also instantites the Config() class so that the config details are 
			available to all commands that inherit the Base class.
		"""
		self.option_dict = option_dict
		self.endpoint = endpoint
		self.config = Config()

	def run(self):
		"""
			Abstract run() method that needs to be implemented in all classes that inherit the Base class.
		"""
		raise NotImplementedError('An implementation of this method has to be provided.')

	def response_handler(self):
		raise NotImplementedError('An implementation of this method has to be provided.')


	def get_arguments(self):
		"""
			This method gives all arguments that are passed on with the entered command.
		"""
		arguments = []
		for key,value in self.option_dict.items():
			if value == True and key not in commands:
				arguments.append(key)
		return arguments

	def system_exit(self):
		"""
			This method performs a safe exit() by either doing a sys.exit() or os.exit() -- usually called during
			keyboard interrupt/ payload request exceptions
		"""
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)

	def config_set(self):
		"""
			This method performs a check to determine if the config file is empty or if the config file has the token
			value set -- called from the Login module
		"""
		if (self.config.config_has_section() and not self.config.get_val_from_config('token')) or (not self.config.config_has_section()):
			return 1
		elif self.config.get_val_from_config('token'):
			iocalls.print_text('\nLogged in as: %s' %self.config.get_val_from_config('username'))
			iocalls.print_text('Session Token: %s' %self.config.get_val_from_config('token'))
			return 0
	
	def login(self):
		"""
			This method takes care of user authentication setup - fetches user input and makes an API request
		"""
		try:
			while True:
				userdata = iocalls.get_user_auth_details()
				payload = apicalls.api_send_request(self.endpoint,'POST',config_data=userdata)
				if payload[0]:
					token = payload[1]['key']
					self.config.update(userdata['username'],token)
					iocalls.print_text('\nantarinX login succesful!\n')
					iocalls.print_text('Logged in as: %s' %userdata['username'])
					iocalls.print_text('Session Token: %s' %token)
					break
				else:
					iocalls.print_text('Invalid username and/or password\n')
		except KeyboardInterrupt:
			print('\n')
			self.system_exit()
			

	def get_env(self):
		if self.config.file_system_env():
			return 'filesystem'
		elif self.config.space_env():
			return 'space'
		elif self.config.cloud_env():
			return 'cloud'

	def display_env(self):
		value = self.get_env().strip()
		if value == 'filesystem':
			message = 'FILE SYSTEM'
		elif value == 'space':
			message = 'SPACE'
		elif value == 'cloud':
			message = 'CLOUD'
		iocalls.print_text(message)

	def display_help(self):
		help_text = __doc__
		iocalls.print_text(help_text)

	def send_request(self,api_endpoint,argument,argval=None,cloud_data=None,pwd=None,packagename=None,shell_command=None):
		config_data_val = dict(self.config.get_values())
		config_data_val['argument'] = argument
		config_data_val['env'] = self.get_env().strip()
		config_data_val['argval'] = argval
		if cloud_data:
			config_data_val['ami_id'] = cloud_data['ami_id'] 
			config_data_val['instance_type'] = cloud_data['instance_type']
			config_data_val['region'] = cloud_data['region']
		if pwd:
			config_data_val['pwd'] = pwd
		if packagename:
			config_data_val['packagename'] = packagename
		if shell_command:
			config_data_val['shell_command'] = shell_command

		payload  = apicalls.api_send_request(api_endpoint,'POST',config_data_val)
		
		return payload

	def quit_env(self,argument=None):
		if not argument:
			value = self.get_env().strip()
		else:
			value = argument
		if value == 'space':
			self.config.quit_space()
		elif value == 'cloud':
			self.config.quit_cloud()

	def has_permissions(self,api_endpoint,argval):
		config_data_val = dict(self.config.get_values())
		config_data_val['argval'] = argval
		payload = apicalls.api_send_request(api_endpoint,'GET',config_data_val)
		if payload[0]:
			return True
		else:
			iocalls.print_text(payload[1]['message'])
			self.system_exit()

	def delete_space(self,api_endpoint,argument,argval):
		if self.has_permissions(api_endpoint,argval):
			if iocalls.get_user_choice():
				pwd = iocalls.get_password()
				payload = self.send_request(api_endpoint,argument,argval,None,pwd)
				print(payload)
				if payload[0]:
					iocalls.print_text("\nProject deleted from antarinX")
				else:
					iocalls.print_text(payload[1]['message'])
				self.system_exit()
	
	def send_upload_request(self,api_endpoint,argval,filename=None):
		config_data_val = dict(self.config.get_values())
		config_data_val['env'] = self.get_env().strip()
		config_data_val['argval'] = argval
		config_data_val['flag'] = 'file'
		if filename:
			config_data_val['newfilename'] = filename	
		payload = apicalls.api_send_request(api_endpoint,'POST',config_data_val,argval)
		if payload[0]:
			if not filename:
				iocalls.print_text('Uploaded file: %s'%argval)
			else:
				iocalls.print_text('Uploaded file: %s'%argval+' as '+filename)
			self.system_exit()
		return payload

	def file_upload(self,api_endpoint,argval):
		payload = self.send_upload_request(api_endpoint,argval)
		while True:
			if not payload[0] and (payload[1]['message']['status_code'] == 400): #duplicate file name
				try:
					iocalls.print_text("\nError: a file with the name already exists in this location.")
					while True:
						if iocalls.get_user_choice_rename():
							new_filename = iocalls.get_new_filename()
							filename = new_filename
							payload = self.send_upload_request(api_endpoint,argval,filename)
							break
				except KeyboardInterrupt:
					print('\n')
					self.system_exit()
			else:
				iocalls.print_text(payload[1]['message'])
				self.system_exit()

	def tree_traversal(self,top, topdown=True, onerror=None, followlinks=False):
		islink, join, isdir = os.path.islink, os.path.join, os.path.isdir
		try:
			names = os.listdir(top)
		except (error,err):
			if onerror is not None:
				onerror(err)
			return
		dirs, nondirs = [], []
		for name in names:
			if isdir(join(top, name)):
				dirs.append(name)
			else:
				nondirs.append(name)
		if topdown:
			yield top, dirs, nondirs

		for name in dirs:
			new_path = join(top, name)
			if followlinks or not islink(new_path):
				for x in self.tree_traversal(self,new_path, topdown, onerror, followlinks):
					yield x
		if not topdown:
			yield top, dirs, nondirs

	def folder_upload_send_request(self,api_endpoint,action,foldername=None,parentdir=None,idval=None,argval=None):
		config_data_val = dict(self.config.get_values())
		config_data_val['flag'] = 'folder'
		action = action.strip()
		config_data_val['action'] = action
		if action == 'create':
			config_data_val['foldername'] = foldername
			config_data_val['parentdir'] = parentdir
		if action == 'upload':
			config_data_val['idval'] = idval
			config_data_val['argval'] = argval
		payload = apicalls.api_send_request(api_endpoint,'POST',config_data_val,argval)
		if payload[0]:
			if action == 'create':
				return payload[1]['id']
			elif action == 'upload':
				return
		else:
			iocalls.print_text(payload[1])
			self.system_exit()

	def folder_upload(self,api_endpoint,filename):
		if filename[-1] == '/':
			filename = filename[:len(filename)-1]
		parentdir = os.path.abspath(os.path.join(filename, os.pardir))
		result = os.walk(filename)
		for root, dirs, files in result:
			pdir = os.path.abspath(os.path.join(root, os.pardir))
			pdir = pdir[len(parentdir):]
			foldername = os.path.basename(root)
			print('Creating directory: ' + os.path.basename(root))
			value = self.folder_upload_send_request(api_endpoint,'create',foldername,pdir)
			files = [f for f in files if f[0] != '.']
			for item in files:
				print('Uploading file: '+ os.path.basename(item))
				argval = os.path.join(root,item)
				self.folder_upload_send_request(api_endpoint,'upload',None,None,value,argval)
			print('\n')

	


