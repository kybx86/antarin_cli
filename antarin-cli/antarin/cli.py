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
  ax env
  ax newproject <projectname>
  ax listprojects
  ax enterproject <projectid>
  ax importdata --file <filename>
  ax importdata --folder <foldername>
  ax addcontributor <username>
  ax deleteproject <projectid>
  ax leaveproject <projectid>
  ax checklog
  ax exitproject
  ax newinstance
  ax listinstances
  ax enterinstance <accesskey>
  ax importfile --algo <filename>
  ax importfile --data <filename>
  ax listfiles --algo
  ax listfiles --data
  ax rmfile --data <filename>
  ax rmfile --algo <filename>
  ax exitinstance
  ax help

"""

from docopt import docopt
from . import __version__ as VERSION
from inspect import getmembers, isclass

def main():

  import commands
  options = docopt(__doc__,version=VERSION)
  #print options
  all_false = 1
  for key, value in options.iteritems():
    if hasattr(commands, key) and value:
      all_false = 0
      module = getattr(commands, key)
      commands = getmembers(module, isclass)
      command = [command[1] for command in commands if command[0] != 'Base' and command[0]!= 'SafeConfigParser'][0] 
      if module.__name__ == 'antarin.commands.upload':
        command = [command[1] for command in commands if command[0] != 'Base' and command[0] != 'MakeDirectory' and command[0]!= 'SafeConfigParser'][0]
      command = command(options)
      command.run()

  # if all_false:
  #   print 'Not a valid command.'
