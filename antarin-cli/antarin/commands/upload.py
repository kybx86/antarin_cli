## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


from .base import Base
from ConfigParser import SafeConfigParser
import json, urllib2, urllib,os
import requests,sys
import gzip
import shutil
from os.path import expanduser
from .mkdir import MakeDirectory
from _color import ax_blue

class Upload(Base):	        

	def file_upload(self,token,filename,name,env_flag,file_flag,id_val=None):
		#print(id_val)
		#url = "http://127.0.0.1:8000/rest-fileupload/"
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-fileupload/"		
		files = {
			'token' : (None, json.dumps(token), 'application/json'),
			'id_val' : (None, json.dumps(id_val), 'application/json'),
			'env_flag':(None,json.dumps(env_flag),'application/json'),
         	'file': (os.path.basename(filename), open(filename, 'rb'), 'application/octet-stream'),
         	'filename':(None,json.dumps(name), 'application/json' ),
         	'file_flag':(None,json.dumps(file_flag),'application/json')
		}
		try:
			connection = requests.put(url, files=files)
		except requests.ConnectionError, e:
			connection = e
			print ax_blue("Error while uploading file %s" %filename)
			print connection 
			sys.exit(1)
		return connection

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
				for x in Upload.tree_traversal(self,new_path, topdown, onerror, followlinks):
					yield x
		if not topdown:
			yield top, dirs, nondirs

	def folder_upload(self, token, foldername, foldername_without_path, id_val, env_flag):
		result = Upload.tree_traversal(self,foldername)
  		key_val = id_val
  		file_flag = 0
  		count = 0
  		makeDirectory = MakeDirectory(Base)
		for root, dirs, files in result:
			
			#print "pk = %s\n"%key_val
			if count!=0:
				alt_foldername = None
				print ax_blue("Creating directory : %s " %os.path.basename(root))
			else:
				alt_foldername = foldername_without_path
				print ax_blue("Creating directory : %s " %foldername_without_path)
			connection = MakeDirectory.send_request(makeDirectory,token,key_val,os.path.basename(root),env_flag,count,alt_foldername)
			if connection.status_code != 200:
				print ax_blue(str(connection.text) + ": while uploading folder %s " %root)
				try:
					sys.exit(0)
				except SystemExit:
					os._exit(0)
			else:
				count = 1
				data = json.loads(json.loads(connection.text)['message'])
				#print data
				file_id_val = data['id']
				if dirs!=[]:
					key_val = data['id']
			for filename in files:
				c = Upload.file_upload(self,token,os.path.join(root, filename),filename,env_flag,file_flag,file_id_val)
				if c.status_code == 204:
					print ax_blue("Uploaded file : %s" %os.path.join(root,filename))
					#print "pk = %s\n"%file_id_val
				else:
					print ax_blue(str(connection) + ":while uploading file %s" %os.path.join(root,filename))


	# i did not add the ax_blue() to the code below because theres a few changes i believe will happen 
	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		error_flag=0
		
		if config.has_section('user_details'):
			token = config.get('user_details', 'token')
			id_val = config.get('user_details','id')
			env_flag = config.get('user_details','PROJECT_ENV')
			if token != "":
				filename = json.loads(json.dumps(self.options))['<file>']
				if os.path.isdir(filename): #--folder
					####TODO: Validation check for filename - should not contain '/'					
					
					#url = "http://127.0.0.1:8000/rest-fileupload/"
					url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-fileupload/"
					
					name = filename
					if filename[-1] == '/':
							filename = filename[:len(filename)-1]
					if name[-1]=='/':
						name = name[:-1]
					foldername = os.path.basename(name)
					payload = {'token':token,'id':id_val,'foldername':foldername}
					try:
						connection = requests.post(url, data = payload)
					except requests.ConnectionError, e:
						connection = e
					if connection.status_code == 400:
						print json.loads(connection.text)
						try:
							while 1:
								user_input = str(raw_input("Do you want to rename the directory? (yes/no) "))
								if user_input == "yes":
									new_filename = str(raw_input("Directory name(cannot be empty) : ")) 
									if new_filename:
										Upload.folder_upload(self,token,filename,new_filename,id_val,env_flag)
										try:
											sys.exit(0)
										except SystemExit:
											os._exit(0)
								elif user_input == "no":
									try:
										sys.exit(0)
									except SystemExit:
										os._exit(0)
								else:
									print "Your response was not one of the expected responses (yes/no)."
						except KeyboardInterrupt:
							print("\n")
							try:
								sys.exit(0)
							except SystemExit:
								os._exit(0)

					if connection.status_code ==200:
						file_flag = 0
						Upload.folder_upload(self,token,filename,foldername,id_val,env_flag)
					else:
						print connection.text
				else:
					file_flag = 1
					name = os.path.basename(filename)
					connection = Upload.file_upload(self,token,filename,name,env_flag,file_flag,id_val)
					if connection.status_code == 204:
						print "Uploaded file : %s" %filename
					elif connection.status_code == 400:#BAD REQUEST -- duplicate filename
						print json.loads(connection.text)
						try:
							while 1:
								user_input = str(raw_input("Do you want to rename the file? (yes/no) "))
								if user_input == "yes":
									new_filename = str(raw_input("File name(cannot be empty) : ")) 
									if new_filename:
										connection = Upload.file_upload(self,token,filename,new_filename,env_flag,file_flag,id_val)
										if connection.status_code == 204:
											print "Uploaded file as : %s" %new_filename
										else:
											print connection.text
										break
								elif user_input == "no":
									break
								else:
									print "Your response was not one of the expected responses (yes/no)."
						except KeyboardInterrupt:
							print("\n")
							try:
								sys.exit(0)
							except SystemExit:
								os._exit(0)

					else:
						print connection.text
			else:
				error_flag=1
		if config.has_section('user_details') == False or error_flag==1:
			print "Error: You are not logged in. Please try this command after authentication--see 'ax login'"

