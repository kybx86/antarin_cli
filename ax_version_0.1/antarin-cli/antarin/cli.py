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
  ax newcloud <name>
  ax listcloud
  ax entercloud <accesskey>
  ax add --env <packagename>
  ax add --algo <path_in_package> <filename>
  ax add --data <path_in_package> <filename>
  ax initialisesession <packagename>
  ax run <shell_command> <packagename>
  ax importfile --algo <filename>
  ax importfile --data <filename>
  ax listfiles --algo
  ax listfiles --data
  ax rmfile --data <filename>
  ax rmfile --algo <filename>
  ax exitcloud
  ax launchinstance <accesskey>
  ax help

"""

from docopt import docopt
from . import __version__ as VERSION
from inspect import getmembers, isclass

def main():

  from . import commands
  options = docopt(__doc__,version=VERSION)
  #print (options)
  #print("\n")

  all_false = 1
  for key, value in options.iteritems():
    #print(key,hasattr(commands,key))
    if hasattr(commands, key) and value:
      print(key,value)
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
