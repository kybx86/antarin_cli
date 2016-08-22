"""
	API call methods
"""

import requests
import json
import os
import sys
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
		if method == 'POST':
			connection = requests.post(URL, data=payload,files=files)
		elif method == 'GET':
			connection = requests.get(URL, data=payload)
		elif method == 'PUT':
			connection = requests.post(URL,data=payload,files=files)
	except requests.exceptions.RequestException as error:
		#log(error) --> implement a logger module
		iocalls.print_exception_error('\nConnection Error : Could not connect to server')
		sys.exit(1)

	message = json.loads(connection.text)
	#print(message)
	if str(connection.status_code)[0] == '2': # --success
		return True,message
	elif str(connection.status_code)[0] == '4': # --failure
		return False,message

