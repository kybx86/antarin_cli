from codecs import open
from os.path import dirname,abspath,join
from setuptools import Command,find_packages,setup
from antarin import __version__


#README.rst is used for documentation
this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
	long_description = file.read()

setup(
    name = 'antarin',
    version = __version__,
    description = 'Antarin Command Line Interface Tool',
    long_description = long_description,
    url = '',
    author = '',
    author_email = '',
    license = '',
    classifiers = [
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords = 'antarin',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires = ['docopt','boto','requests'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points = {
        'console_scripts': [
            'antarin=antarin.cli:main',
        ],
    },
   
)