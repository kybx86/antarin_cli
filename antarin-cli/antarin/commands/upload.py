
from .base import Base
from ConfigParser import SafeConfigParser
import json, urllib2, urllib,os
import requests,sys
import gzip
import shutil
from os.path import expanduser

class Upload(Base):	        

	def file_upload(self,token,filename,id_val=None):
		#print id_val
		url = "http://webapp-test.us-west-2.elasticbeanstalk.com/rest-fileupload/"		
		files = {
			'token' : (None, json.dumps(token), 'application/json'),
			'id_val' : (None, json.dumps(id_val), 'application/json'),
         	'file': (os.path.basename(filename), open(filename, 'rb'), 'application/octet-stream')
		}
		try:
			connection = requests.put(url, files=files)
		except requests.ConnectionError, e:
			connection = e
			print "Error while uploading file %s" %filename
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

	def folder_upload(self,token,foldername):
		result = Upload.tree_traversal(self,foldername)
		#request_val = Upload.send_request(self,token,result)
		# try:
		# 	request_val = requests.put("http://127.0.0.1:8000/rest-fileupload/", data = {'dir_structure':result})
		# except requests.ConnectionError, e:
		# 	connection = e
		# 	print "Could not connect to server"
		# 	print connection 
		# 	sys.exit(1)
		for root, dirs, files in result:
			for name in files:
				c = Upload.file_upload(self,token,os.path.join(root, name))
				if c.status_code == 204:
					print "Uploaded file : %s" %os.path.join(root, name)

	def run(self):
		config = SafeConfigParser()
		home_path = expanduser("~")
		filepath = home_path + '/.antarin_config.ini'
		config.read(filepath)
		token = config.get('user_details', 'token')
		id_val = config.get('user_details','id')
		if token != "":
			filename = json.loads(json.dumps(self.options))['<file>']
			if os.path.isdir(filename):
				Upload.folder_upload(self,token,filename)
			else:
				connection = Upload.file_upload(self,token,filename,id_val)
				if connection.status_code == 204:
					print "Uploaded file : %s" %filename
				else:
					print connection
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."


