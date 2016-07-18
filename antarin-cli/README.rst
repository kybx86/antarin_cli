ANTARIN command line interface tool

Installation:

1. cd antarin-cli
2. pip install .

Usage:

 1. ax login
  	This will prompt you to enter your antarin credentials (username and password). After successful authentication, an authentication token and other user account details will be stored in a local config file.

 2. ax logout
 	To logout of your antarin account from the CLI tool.

 3. ax ls
  	Lists all files/folders inside current directory
  
 4. ax pwd
 	Gives current working directory

 5. ax upload <file>
 	To upload a file inside your current working directory. Provide the name of the file to be uploaded as a positional argument to the command. [ antarin upload myfile.txt ]

 6. ax cd
 	Navigate to home directory

 	ax cd ..
 	Change directory to immediate parent directory

 	ax cd <foldername> 
 	[Currently works for relative path only]
 	Change directory to a child directory(specified by foldername) that is inside your current working directory

 7. ax mkdir <foldername>
 	To create a new directory inside your current working directory

 8. ax -h | --help
 	Lists all available commands for the CLI tool along with their usage patterns.
 
 9. ax --version
 	Shows the version of the CLI tool that is currently running on your machine

 10. ax summary
 	Gives a summary of the user account/details

Options:
  -h --help                         Show this screen.
  --version                         Show version.