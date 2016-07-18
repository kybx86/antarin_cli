
from .base import Base
from ConfigParser import SafeConfigParser
import json, urllib2, urllib,os
import requests,sys
import gzip
import shutil
from os.path import expanduser
from .mkdir import MakeDirectory

class Upload(Base):	        

	def file_upload(self,token,filename,id_val=None):
		#url = "http://127.0.0.1:8000/rest-fileupload/"
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

	def folder_upload(self,token,foldername,id_val):
		result = Upload.tree_traversal(self,foldername)
  		key_val = id_val
  		makeDirectory = MakeDirectory(Base)
		for root, dirs, files in result:
			print "Creating directory %s" %os.path.basename(root)
			connection = MakeDirectory.send_request(makeDirectory,token,key_val,os.path.basename(root))
			if connection.status_code != 200:
				print str(connection) + ": while uploading folder %s " %root
			else:
				data = json.loads(json.loads(connection.text))
				key_val = data['id']
			for filename in files:
				c = Upload.file_upload(self,token,os.path.join(root, filename),key_val)
				if c.status_code == 204:
					print "Uploaded file : %s" %os.path.join(root,filename)
				else:
					print str(connection) + ":while uploading file %s" %os.path.join(root,filename)

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
				if filename[-1] == '/':
					filename = filename[:len(filename)-1]
				Upload.folder_upload(self,token,filename,id_val)
			else:
				connection = Upload.file_upload(self,token,filename,id_val)
				if connection.status_code == 204:
					print "Uploaded file : %s" %filename
				else:
					print connection
		else:
			print "Looks like you have not verified your login credentials yet.Please try this command after authetication is compelete."


