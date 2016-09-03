
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

def file_DoesNotExist():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "File does not exist."
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

def package_DoesNotExist(packagename=None):
	return_dict = {}
	return_dict['status_code'] = 400
	if packagename:
		return_dict['message'] = message + "Package %s does not exist in the cloud." %packagename
	else:
		return_dict['message'] = message + "Package does not exist in the cloud."
	return return_dict

def folder_exists():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Folder with the same name exists."
	return return_dict

def file_exists():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "File with the same name exists."
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

def permission_denied():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Permission denied."
	return return_dict

def incorrect_password():
	return_dict = {}
	return_dict['status_code'] = 404
	return_dict['message'] = message + "Invalid password."
	return return_dict

def user_DoesNotExist():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "No antarinX user found with specified username."
	return return_dict

def cloud_notRunning():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Cloud is not in 'running' state"
	return return_dict

def intance_launch_error():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "There was a problem during initialization of the cloud."
	return return_dict

def contributor_exists():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Specified user is already a contributor to this space."
	return return_dict

def package_exists():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Package with same name exists in the cloud."
	return return_dict
	
def instance_not_running():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Cloud not in running state."
	return return_dict


def no_data_folder():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "'data' folder not found in package."
	return return_dict

def no_requirements_file():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "'requirements.txt' file not found in package."
	return return_dict

def wrong_path_specified():
	return_dict = {}
	return_dict['status_code'] = 400
	return_dict['message'] = message + "Path specified is not correct."
	return return_dict