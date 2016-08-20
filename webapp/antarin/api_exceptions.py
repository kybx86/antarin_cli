
message = 'Error: '

def project_DoesNotExist():
	return_dict = {}
	return_dict['status_code'] = 404
	return_dict['message'] = message + "Space does not exist. Not a valid access key"

	return return_dict

def invalid_session_token():
	return_dict = {}
	return_dict['status_code'] = 404
	return_dict['message'] = message + "Session Token is not valid."

	return return_dict

def folder_DoesNotExist():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Folder does not exist."
	return return_dict

def instance_DoesNotExist():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Instance does not exist. Not a valid access key"
	return return_dict
	
def folder_exists():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Folder with the same name exists."
	return return_dict

def project_exists():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Project with the same name exists."
	return return_dict

def instance_exists():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Cloud with the same name exists in this project environment."
	return return_dict