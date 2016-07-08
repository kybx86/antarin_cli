ANTARIN command line interface tool

Installation:

1. cd antarin-cli
2. pip install .

Usage:

 1. antarin login
  	This will prompt you to enter your antarin credentials (username and password). After successful authentication, an authentication token and other user account details will be stored in a local config file.

 2. antarin logout
 	To logout of your antarin account from the CLI tool.

 3. antarin ls
  	Lists all files/folders in your antarin account
  
 4. antarin upload <file>
 	To upload a file from your system to the antarin server. Provide the name of the file to be uplaoded as a positional argument to the command. [ antarin upload myfile.txt ]

 5. antarin -h | --help
 	Lists all available commands for the CLI tool along with their usage patterns.
 
 6. antarin --version
 	Shows the version of the CLI tool that is currently running on your machine

Options:
  -h --help                         Show this screen.
  --version                         Show version.