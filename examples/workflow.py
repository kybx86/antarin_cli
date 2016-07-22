## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##


# -- Example: 
# This python file demonstrates a direct workflow integration using the antarin API
#		- A given experimental result is produced from 'def produce_data'. This is 
#		- then written to folder in the users local system. Finally, the user uploads
#		- the results using the antarin upload API 
#

import antarin.upload as ax
import os
import numpy as np 


PROJECT_FOLDER = '/Users/kevinyedidbotton/Desktop/antarin_folder'

def produce_data(m,n):
	data = np.random.rand(m,n)
	return data


def write_to_file(file_name, data_input):
	full_path = os.path.join(PROJECT_FOLDER,file_name)
	with open(full_path, "w") as output:
		np.savetxt(output, data_input) # saving data to file in local custom folder  'antarin_folder'
	return full_path

def upload_to_antarin(path):
	upload_obj = ax.Upload(path)
	upload_obj.submit()




def run():

	# --some 'experimental' data
	data = produce_data(50,40)

	# -- saving data to txt file
	path = write_to_file('experiment1_results.txt', data)

	# -- antarin upload 
	upload_to_antarin(path)


def main():
	run()

if __name__ == '__main__':
	main()