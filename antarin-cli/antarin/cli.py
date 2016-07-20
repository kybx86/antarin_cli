## -- Copyright (c) 2016 Antarin Technologies Inc. -- ##

"""
antarinX

Usage:
  ax login
  ax summary
  ax -h | --help
  ax ls
  ax pwd
  ax cd [<foldername>]
  ax rm [-r] <folder/file>
  ax mkdir <foldername>
  ax upload <file>
  ax --version
  ax logout
  
"""

# Usage:
#   ax login
#   ax logout
#   ax summary
#   ax ls
#   ax cd [<foldername>]
#   ax pwd
#   ax rm [-r] <folder/file>
#   ax mkdir <foldername>
#   ax upload <file>
#   ax download <file>
#   ax delete <file>
#   ax -h | --help
#   ax --version

from docopt import docopt
from . import __version__ as VERSION
from inspect import getmembers, isclass
import sys

def main():

  import commands
  options = docopt(__doc__,version=VERSION)
  #print options
  for key, value in options.iteritems():
    if hasattr(commands, key) and value:
      module = getattr(commands, key)
      commands = getmembers(module, isclass)
      #print commands
      command = [command[1] for command in commands if command[0] != 'Base' and command[0]!= 'SafeConfigParser'][0] 
      if module.__name__ == 'antarin.commands.upload':
        command = [command[1] for command in commands if command[0] != 'Base' and command[0] != 'MakeDirectory' and command[0]!= 'SafeConfigParser'][0]
      command = command(options)
      #print command
      command.run()

##Python 3.5
  # import subprocess
  # options = docopt(__doc__,version=VERSION)

  # for key, value in options.items():
  #   if hasattr(subprocess, key) and value:
  #     module = getattr(subprocess, key)
  #     #print module
  #     commands = getmembers(module, isclass)
  #     print commands
  #     command = [command[1] for command in commands if command[0] != 'Base' and command[0]!= 'SafeConfigParser'][0] 
  #     command = command(options)
  #     command.run()

