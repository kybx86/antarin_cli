## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##

#!/bin/sh
 
#echo "Hello, world!"
if pip freeze| grep 'antarin'
then
	pip uninstall antarin
	pip install .
	clear
else
	pip install .
fi

