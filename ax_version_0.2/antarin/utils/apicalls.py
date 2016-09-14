"""
	API call methods
"""

import requests
import json
import os
import sys
import time 
from .. import config
from . import iocalls

def api_send_auth_request(api_endpoint,method=None,config_data=None):
	pass

def api_send_request(api_endpoint,method=None,config_data=None,file=None):
	payload = config_data
	URL = config.URL + api_endpoint
	if file:
		files = {
		'file': (os.path.basename(file), open(file, 'rb')),
		}
	else:
		files = None
	try:

		if api_endpoint == '/initialize/':
			iocalls.print_text("Initializing session...\nINFO: This may take a few minutes--use 'ax monitor' to see session status")
			requests.post(URL, data=payload,files=files,timeout=30) 

		if method == 'POST':
			connection = requests.post(URL, data=payload,files=files)
		elif method == 'GET':
			connection = requests.get(URL, data=payload)
		elif method == 'PUT':
			connection = requests.post(URL,data=payload,files=files)

		# if api_endpoint == '/initialize/':
		# 	# -- Note:
		# 	#	timeout is not a time limit on the entire response download;
		# 	#   rather, an exception is raised if the server has not issued a response
		# 	#   for timeout seconds (more precisely, if no bytes have been received on 
		# 	#   the underlying socket for timeout seconds). If no timeout is specified 
		# 	#   explicitly, requests do not time out.

		# 	requests.post(URL, data=payload,files=files,timeout=30) # Error with AWS
		# 	connection = requests.post(URL, data=payload,files=files)
			

		# elif method == 'POST':
		# 	connection = requests.post(URL, data=payload,files=files)
		# elif method == 'GET':
		# 	connection = requests.get(URL, data=payload)
		# elif method == 'PUT':
		# 	connection = requests.post(URL,data=payload,files=files)
	
	except requests.exceptions.Timeout:
		sys.exit(0)
	except requests.exceptions.RequestException as error:
		#log(error) --> implement a logger module
		iocalls.print_exception_error('\nConnection Error: Could not connect to antarin server')
		sys.exit(1)

	# print(connection)	
	message = json.loads(connection.text)

	if str(connection.status_code)[0] == '2': # --success
		return True,message
	elif str(connection.status_code)[0] == '4': # --failure
		return False,message

