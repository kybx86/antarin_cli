"""
antarinX setup requirements
"""

import os
from setuptools import setup,find_packages
from antarin import __version__


current_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_directory,'readme.rst')) as f:
	long_description = f.read()

setup(
	name = 'antarinX',
	version = __version__,
	description = 'antarinX Command Line Interface Tool',
	long_description = long_description,
	packages = ['antarin','antarin.commands','antarin.utils'],
	package_data={},
	include_packaged_data = True,
	keywords = 'ax',
	install_requires = ['docopt','requests','termcolor'],
	entry_points = {
        'console_scripts': [
            'ax = antarin.__main__:main',
       		],
    	},
	)
