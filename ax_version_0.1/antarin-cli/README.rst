ANTARIN command line interface tool

Installation:

1. cd antarin-cli
2. pip install .

Usage: 
	
	Filesystem Tools: 

		- To login into your antarinX account: 
		
			$ ax login 


		- To view account summary:
			
			$ ax summary 


		- To view your files and folders: 
		
			$ ax ls


		- To view current directory:
		
			$ ax pwd 


		- To change directory:
		
			$ ax cd [<foldername>]


		- To delete filers or folders:
		
			$ ax rm [-r] <folder/file>


		- To create new directory:
		
			$ ax mkdir <foldername>


		- To upload new file or folder from local system:
			
			$ ax upload <folder/file>


		- To logout from antarinX account 
			
			$ ax logout 



	Project Tools: 

		- To create new project: 

			$ ax newproject <projectname>


		- To view projects you created or belong to: 
		
			$ ax listprojects


		- To enter into a project you created or belong to:
			
			$ ax enterproject <projectname>


		- To import a file from your account into a project:
		
			$ ax importdata --file <filename>


		- To import a folder from your account into a project:
			
			$ ax importdata --folder <foldername>


		- To add contributor to project: 
		
			$ ax addcontributor <username>


		- To view project summary: 
			
			$ ax summary 

		- To view a project's files and folders:
			
			$ ax ls

		- To chage directory within project: 

			$ ax cd [<foldername>]

		- To create directory within project: 

			$ ax mkdir <foldername>


		- To delete file or folder from project: 
		
			$ ax rm [-r] <folder/file>


		- (Caution) To completely delete project from antarinX and all associated files and contributors: 

			$ ax deleteproject <projectname>


		- To remove yourself from a project as a contributor: 

			$ ax leaveproject <projectname>


		- To view project timeline changes: 

			$ ax checklogs
			

		- To exit project: 

			$ ax exitproject








Options:
  -h --help                         Show this screen.
  --version                         Show version.