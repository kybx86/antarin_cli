import calendar
from datetime import datetime


# still working on it--but it works.  


# t_utc = datetime.utcnow() #datetime obj
# t_now_ts = calendar.timegm(t_utc.timetuple()) #numeric format
# t_now = datetime.fromtimestamp(t_now_ts)
# # format = "%Y-%m-%d %H:%M:%S %Z"
# format = "%a, %d %b %Y %H:%M:%S"
# time = t_now.strftime(format).rstrip()
# print(time)


def utc_to_local(utc_string):
	# utc_string = '[24/August/2016 16:58:49]'
	utc_string = utc_string.strip("[]")
	input_format  = "%d/%B/%Y %H:%M:%S"
	output_format = "%a, %d %b %Y %H:%M:%S"
	t_utc = datetime.strptime(utc_string, input_format)
	t_local_ts = calendar.timegm(t_utc.timetuple())
	t_local = datetime.fromtimestamp(t_local_ts)
	t_local = t_local.strftime(output_format).rstrip()
	return t_local
