"""
	Base class for all antarinX commands
"""

#from __future__ import division 

import os, sys, json, time
from ..__main__ import __doc__
from ..config import Config
from ..utils import iocalls,apicalls
from ..utils import _color as cl



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
					iocalls.print_login(userdata['username'], token)
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
			message = 'enviroment: Filesystem'
		elif value == 'space':
			message = 'enviroment: Space'
		elif value == 'cloud':
			message = 'enviroment: Cloud'
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
			iocalls.print_text('Exited space enviroment.')
		elif value == 'cloud':
			self.config.quit_cloud()
			iocalls.print_text('Exited cloud enviroment.')

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
				if payload[0]:
					iocalls.print_text("Project deleted.")
				else:
					iocalls.print_text(payload[1]['message'])
				self.system_exit()

	def get_size(self, file=None, num_bytes=None):

		if file is not None and num_bytes is None:
			file_size = os.stat(file).st_size
		elif num_bytes is not None:
			file_size = num_bytes
		if file_size >0 and file_size <1e3:
			file_size *= 1
			unit = 'bytes'
		elif file_size >= 0 and file_size < 1e6:
			file_size *= 1e-3
			unit = 'KB'
		elif file_size >= 1e6 and file_size < 1e9:
			file_size *= 1e-6
			unit = 'MB'
		elif file_size >= 1e9 and file_size < 1e12:
			file_size *= 1e-9
			unit = 'GB'
		elif file_size >= 1e12 and file_size < 1e15:
			file_size *= 1e-12
			unit = 'TB'
		return file_size, unit 

	def get_time(self, time_elapsed):
		if time_elapsed >= 0 and time_elapsed <60:
			time = time_elapsed
			unit = 'seconds'
		elif time_elapsed >= 60:
			time = time_elapsed / 60
			unit = 'minutes'
		elif time_elapsed >= 3600:
			time = time_elapsed / 60
			time /= 60
			unit = 'hours' 
		return time, unit

	def send_upload_request(self, api_endpoint, argval, filename=None):
		config_data_val = dict(self.config.get_values())
		config_data_val['env'] = self.get_env().strip()
		config_data_val['argval'] = argval
		config_data_val['flag'] = 'file'
		if filename:
			config_data_val['newfilename'] = filename
		file_size, unit = self.get_size(file=argval, num_bytes=None)
		cl.out(cl.blue('\nUploading 1/1 files | Size {0:.2f} {1}:\t{2} ...\n').format(file_size, unit, argval))
		time_initial = time.time()
		payload = apicalls.api_send_request(api_endpoint, 'POST', config_data_val, argval)
		time_elapsed = time.time() - time_initial
		time_elapsed, unit = self.get_time(time_elapsed)

		if payload[0]:
			if not filename:
				cl.out(cl.blue('\nUploaded file: {0}\n').format(argval))
			else:
				cl.out(cl.blue('\nUploaded file: {0} as {1}\n').format(argval,filename))
			cl.out(cl.blue('Time elapsed: {0:.2f} {1}\n').format(time_elapsed,unit))
			self.system_exit()
		return payload

	def file_upload(self,api_endpoint,argval):
		payload = self.send_upload_request(api_endpoint,argval)
		while True:
			if not payload[0] and (payload[1]['message']['status_code'] == 400): #duplicate file name
				try:
					iocalls.print_text("Error: a file with the name already exists in this location.")
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

	def get_walk_counts(self, os_walk):
		# Args: generator tuple from native os.walk

		# bfs = list(os_walk)
		bfs = os_walk
		file_counter = 0
		dir_counter = 1
		bytes_counter = 0
		for i in range(len(bfs)):
			dir_counter  += len(bfs[i][1])
			file_counter += len(bfs[i][2]) #also counts .hidden files
			for file in range(len(bfs[i][2])):
				file_path = os.path.join(bfs[i][0], bfs[i][2][file])
				num_bytes = os.stat(file_path).st_size
				bytes_counter += num_bytes

		return file_counter, dir_counter, bytes_counter

	def folder_upload(self,api_endpoint,filename):
		if filename[-1] == '/':
			filename = filename[:len(filename)-1]

		parentdir = os.path.abspath(os.path.join(filename, os.pardir))
		result = list(os.walk(filename)) # generator to list ->for multiple usages
		num_files, num_dirs, num_bytes = self.get_walk_counts(result)
		folder_size, unit = self.get_size(file=None, num_bytes=num_bytes)
		cl.out(cl.blue('\nUploading folder: {0} ...\n').format(filename))
		cl.out(cl.blue('\nFolder size: {0:.2f} {1}').format(folder_size ,unit))
		print()
		bytes_uploaded = 0
		time_initial = time.time()
		for root, dirs, files in result:
			pdir = os.path.abspath(os.path.join(root, os.pardir))
			pdir = pdir[len(parentdir):]
			foldername = os.path.basename(root)
			value = self.folder_upload_send_request(api_endpoint, 'create', foldername, pdir)			
			# files = [f for f in files if f[0] != '.'] #keeping .files is important, in some cases
			files = [f for f in files] 
			for item in files:
				argval = os.path.join(root,item)
				bytes_uploaded += os.stat(argval).st_size
				self.folder_upload_send_request(api_endpoint, 'upload', None, None, value, argval)
				percentage = round((bytes_uploaded / num_bytes)*100)					
				cl.out(cl.blue('\rUploaded: {0:.0f}% | {1} / {2} {3:.60s}').format(percentage, bytes_uploaded, num_bytes, 'bytes'))
				sys.stdout.flush()
		# print
		time_elapsed = time.time() - time_initial
		time_elapsed, unit = self.get_time(time_elapsed)
		cl.out(cl.blue('\nTime elapsed: {0:.2f} {1}').format(time_elapsed,unit))
		cl.out(cl.blue('\nUpload complete!\n'))
		# print('\n')
	


