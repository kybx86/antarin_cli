
from datetime import datetime
import calendar
import os




# t_utc = datetime.utcnow() #datetime obj
# t_now_ts = calendar.timegm(t_utc.timetuple()) #numeric format
# t_now = datetime.fromtimestamp(t_now_ts)
# # format = "%Y-%m-%d %H:%M:%S %Z"
# format = "%a, %d %b %Y %H:%M:%S"
# time = t_now.strftime(format).rstrip()
# print(time)


def utc_to_local(utc_string):
	utc_string = utc_string.strip("[]")
	input_format  = "%d/%B/%Y %H:%M:%S"
	output_format = "%a, %d %b %Y %H:%M:%S"
	t_utc = datetime.strptime(utc_string, input_format)
	t_local_ts = calendar.timegm(t_utc.timetuple())
	t_local = datetime.fromtimestamp(t_local_ts)
	t_local = t_local.strftime(output_format).rstrip()
	return t_local


def check_name_size(message, dtype): 

	if dtype == 'space' or dtype == 'cloud':
		SIZE_LIM = 15
		max_size = 0
		for item in range(len(message)):
			entry = message[item]
			entry = entry.split('\t')
			if dtype == 'space':
				name = entry[0].split(':')[1]
			elif dtype == 'cloud':
				name = entry[0]
			size = len(name)
			if size > max_size:
				max_size = size
		if max_size > SIZE_LIM:
			return SIZE_LIM
		else:
			return max_size
	elif dtype == 'monitor':
		SIZE_LIM = 15
		OWNER_SIZE_LIM = 30
		sizes = {}
		max_size_cloud = 0
		max_size_space = 0
		max_size_owner = 0
		for item in message:
			cloud_name = item[0]
			# owner_name = item[1].split(':')[0] #space owner
			owner_name = item[3] #cloud owner
			space_name = item[1].split(':')[1]
			cloud_size = len(cloud_name)
			owner_size = len(owner_name)
			space_size = len(space_name)

			if cloud_size > max_size_cloud:
				max_size_cloud = cloud_size
			if owner_size > max_size_owner:
				max_size_owner = owner_size
			if space_size > max_size_space:
				max_size_space = space_size

		if max_size_cloud > SIZE_LIM:
			sizes['cloud_size'] = SIZE_LIM 
		else:
			sizes['cloud_size'] = max_size_cloud

		if max_size_owner > OWNER_SIZE_LIM:
			sizes['owner_size'] = OWNER_SIZE_LIM 
		else:
			sizes['owner_size'] = max_size_owner

		if max_size_space > SIZE_LIM:
			sizes['space_size'] = SIZE_LIM
		else: 
			sizes['space_size'] = max_size_space

		return sizes




def get_time(time_elapsed): 
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


def get_size(file=None, num_bytes=None): 

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