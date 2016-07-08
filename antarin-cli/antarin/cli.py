"""
antarin

Usage:
  antarin hello
  antarin login
  antarin logout
  antarin summary
  antarin ls
  antarin upload <file>
  antarin download <file>
  antarin -h | --help
  antarin --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
Examples:
  antarin login
  antarin summary
"""

from docopt import docopt
from . import __version__ as VERSION
from inspect import getmembers, isclass

def main():

  import commands
  options = docopt(__doc__,version=VERSION)

  for key, value in options.iteritems():
    if hasattr(commands, key) and value:
      module = getattr(commands, key)
      #print module
      commands = getmembers(module, isclass)
      #print commands
      command = [command[1] for command in commands if command[0] != 'Base' and command[0]!= 'SafeConfigParser'][0] 
      command = command(options)
      command.run()