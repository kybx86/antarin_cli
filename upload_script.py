#!/usr/bin/python

"""
	Run:
	$python upload_script.py <path_to_file/folder>

"""
from antarin.upload import Upload
import sys
path = sys.argv[1]

upload_obj = Upload(path)
upload_obj.submit()

