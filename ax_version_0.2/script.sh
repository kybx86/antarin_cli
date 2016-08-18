#!/bin/sh
 
if pip freeze| grep 'antarin'
then
	#pip uninstall -r requirements.txt
	pip uninstall antarinX
	pip install .
	clear
else
	pip install .
fi

