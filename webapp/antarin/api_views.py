import hashlib,random,json,boto,os
import boto3,sys,time
from django.utils import timezone
from django.conf import settings
from hurry.filesize import size
from boto.s3.connection import S3Connection, Bucket, Key
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from fabric.context_managers import settings as fabric_settings
from fabric.api import hosts,env,run
from fabric.network import disconnect_all
from fabric.tasks import execute
from fabric.exceptions import NetworkError
from fabric.state import connections
from antarin import api_exceptions
from antarin.models import *

#S3 Bucket details
conn = S3Connection(settings.AWS_ACCESS_KEY_ID , settings.AWS_SECRET_ACCESS_KEY)
b = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
k = Key(b)


key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'ec2test.pem')

class LogoutView(APIView):
	def post(self,request):
		print('token='+self.request.data['token'])
		try:
			instance = Token.objects.get(key=self.request.data['token'])
			instance.delete()
			message = {'message':'antarinX logout succesful!'+ '\n' + 'Deleted token and user account details.'}
			return Response(message,status=200)
		except Token.DoesNotExist:
			print('here')
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class NewView(APIView):
	def generate_rand(n):
		llimit = 10**(n-1)
		ulimit = (10**n)-1
		return random.randint(llimit,ulimit)

	def new_folder(user_object,value,id_val):
		pk = id_val
		foldername = value
		if pk != "":
			user_folder_object = user_object.user.user_folders.get(pk=int(pk))
			antarin_folder_object = user_folder_object.folder_ref
		else:
			antarin_folder_object = None

		all_user_folders = user_object.user.user_folders.all()
		#all_files_in_currdir = user_object.user.all_antarin_files.filter(folder=antarin_folder_object)
		
		dup_name_flag = 0
		for item in all_user_folders:
			if item.folder_ref.parentfolder==antarin_folder_object and item.folder_ref.name == foldername:
				dup_name_flag = 1
				break
		if dup_name_flag:
			message = api_exceptions.folder_exists()
			return message

		new_antarin_folder_object = AntarinFolders(user=user_object.user,name=foldername,parentfolder=antarin_folder_object)
		new_antarin_folder_object.save()
		new_user_folder_object = UserFolders(user=user_object.user,folder_ref=new_antarin_folder_object)
		new_user_folder_object.save()
		data = {'id':new_user_folder_object.pk}
		print(data)
		message = {'message':json.dumps(data),'status_code':200}		
		return message

	def new_project(user_object,argval):
		projectname = argval
		try:
			projectname = user_object.user.username + ':' + projectname
			
			#create project object
			new_project_object = AntarinProjects(name=projectname)
			new_project_object.save()
			
			#generate accesskey
			all_user_projects = user_object.user.user_projects.all()
			accesskey_list = []
			for item in all_user_projects:
				accesskey_list.append(item.access_key)

			num = NewView.generate_rand(3)
			while num in accesskey_list:
				num = NewView.generate_rand(3)

			access_key = num

			#create userprojects object
			new_userprojects_object = UserProjects(user=user_object.user,project=new_project_object,status='A',access_key=access_key)
			new_userprojects_object.save()
			
			#add to logs
			new_projectlogs_object = AntarinProjectLogs(user=user_object.user,project=new_project_object,action=user_object.user.username + ' created '+ projectname)
			new_projectlogs_object.save()
			
			data = {'projectname':new_project_object.name,'access_key':access_key}
			message = {'message':data,'status_code':200}
			return message
		except IntegrityError:
			message = api_exceptions.project_exists()
			return message
		

	def new_cloud(user_object,spacename,argval,ami_id,instance_type,region):
		projectname = spacename
		instance_name = argval

		project_object = AntarinProjects.objects.get(name=projectname)
		all_project_clouds = project_object.project_clouds.all()
		
		dup_name_flag = 0
		for  item in all_project_clouds:
			if item.cloud_name == instance_name:
				dup_name_flag = 1
				break
				print("duplicate names")
		
		if dup_name_flag:
			message = api_exceptions.instance_exists()
			return message

		accesskey_list = []
		for item in all_project_clouds:
			accesskey_list.append(item.access_key)

		num = NewView.generate_rand(3)
		while num in accesskey_list:
			num = generate_rand(3)

		access_key = num
		print(access_key)

		new_cloud_object = AntarinProjectClouds(project=project_object,cloud_name=instance_name,ami_id=ami_id,region=region,instance_type=instance_type,access_key=access_key)
		#new_instances_object = UserInstances(user=user_object.user,project=project_object,instance_name=instance_name,ami_id=ami_id,region=region,instance_type=instance_type,access_key=access_key)
		new_cloud_object.save()

		new_user_cloud_object = UserClouds(user=user_object.user,cloud=new_cloud_object)
		new_user_cloud_object.save()

		new_projectlogs_object = AntarinProjectLogs(user=user_object.user,project=project_object,action=user_object.user.username + ' created cloud '+ new_cloud_object.cloud_name)
		new_projectlogs_object.save()

		message={'message':'New cloud details were recorded','access_key':new_cloud_object.access_key,'status_code':200}
		return message

	def post(self,request):
		token = self.request.data['token']
		argument = self.request.data['argument'].strip()
		argval = self.request.data['argval'].strip()

		try:
			user_object = Token.objects.get(key=token)
			if argument == 'folder':
				dir_id = self.request.data['id']
				return_val = NewView.new_folder(user_object,argval,dir_id)
				
			if argument == 'space':
				return_val = NewView.new_project(user_object,argval)

			if argument == 'cloud':
				ami_id = self.request.data['ami_id'].strip()
				instance_type = self.request.data['instance_type'].strip()
				region = self.request.data['region'].strip()
				spacename = self.request.data['spacename'].strip()
				return_val = NewView.new_cloud(user_object,spacename,argval,ami_id,instance_type,region)
			
			message = {'message':return_val['message']}
			if return_val['status_code'] == 200:
				return Response(message,200)
			elif return_val['status_code'] == 400:
				return Response(message,400)

		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class UploadView(APIView):

	def calculate_used_data_storage(all_files):
		#print(all_files)
		total_val = 0
		for file in all_files:
			total_val = total_val + file.file.size
		return size(total_val)

	def add_file(user_object,file_object,filename,id_val):
		pk = id_val

		filename = os.path.basename(filename)
		if pk != "":
			user_folder_object = user_object.user.user_folders.get(pk=int(pk))
			antarin_folder_object = user_folder_object.folder_ref
		else:
			antarin_folder_object = None

		all_user_files = user_object.user.user_files.all()
		#all_files_in_currdir = user_object.user.all_antarin_files.filter(folder=antarin_folder_object)
		
		dup_name_flag = 0
		for item in all_user_files:
			if item.file_ref.folder==antarin_folder_object and os.path.basename(item.file_ref.file.file.name) == filename:
				dup_name_flag = 1
				break
		if dup_name_flag:
			message = api_exceptions.file_exists()
			return message

		antarin_files = AntarinFiles()
		antarin_files.user = user_object.user
		antarin_files.file = file_object
		antarin_files.file.name = filename
		antarin_files.folder = antarin_folder_object
		
		all_files = user_object.user.all_antarin_files.all()
		used_data_storage = UploadView.calculate_used_data_storage(all_files)
		user_object.user.userprofile.data_storage_used = str(used_data_storage)
		user_object.user.save()
		user_object.user.userprofile.save()
		antarin_files.save()
		
		user_files_object = UserFiles(user=user_object.user,file_ref=antarin_files)
		user_files_object.save()
		#catch error when save didn't work fine and return status 400
		print("\n")
		message = {'message':"File upload successful.",'status_code':200}
		return message

	def add_file_folder(user_object,file_object,filename,id_val):
		
		pk = id_val
		
		filename = os.path.basename(filename)
		if pk != "":
			user_folder_object = user_object.user.user_folders.get(pk=int(pk))
			antarin_folder_object = user_folder_object.folder_ref
		else:
			
			antarin_folder_object = None

		antarin_files = AntarinFiles()
		antarin_files.user = user_object.user
		antarin_files.file = file_object
		antarin_files.file.name = filename
		antarin_files.folder = antarin_folder_object
		
		all_files = user_object.user.all_antarin_files.all()
		used_data_storage = UploadView.calculate_used_data_storage(all_files)
		user_object.user.userprofile.data_storage_used = str(used_data_storage)
		user_object.user.save()
		user_object.user.userprofile.save()
		antarin_files.save()
		
		user_files_object = UserFiles(user=user_object.user,file_ref=antarin_files)
		user_files_object.save()
		#catch error when save didn't work fine and return status 400
		print("\n")
		message = {'message':"File upload successful.",'status_code':200}
		return message

	def get_parentdir_id(user_object,parentpath,id_val):
		if parentpath[0] == '/':
			parentpath = parentpath[1:]
		l = parentpath.split('/')
		if id_val:
			id_val = int(id_val)
			for item in l:
				user_folder_object = user_object.user.user_folders.get(pk=int(id_val))
				antarin_folder_object = user_folder_object.folder_ref
				next_folder_object = antarin_folder_object.parent_folder_reference.get(name=item)
				id_val = user_object.user.user_folders.get(folder_ref=next_folder_object).pk
				#id_val = next_folder_object.pk
		else:
			antarin_folder_object = AntarinFolders.objects.get(user=user_object.user,name=l[0],parentfolder=None)
			id_val = user_object.user.user_folders.get(folder_ref=antarin_folder_object).pk
			for item in l[1:]:
				next_folder_object = antarin_folder_object.parent_folder_reference.get(name=item)
				id_val = user_object.user.user_folders.get(folder_ref=next_folder_object).pk
				user_folder_object = user_object.user.user_folders.get(pk=id_val)
				antarin_folder_object = user_folder_object.folder_ref

		return str(id_val)

	def create_folder(user_object,foldername,parentdir,id_val):
		pk = id_val

		if not parentdir:
			if pk != "":
				user_folder_object = user_object.user.user_folders.get(pk=int(pk))
				antarin_folder_object = user_folder_object.folder_ref
			else:
				antarin_folder_object = None

			all_user_folders = user_object.user.user_folders.all()
			#all_files_in_currdir = user_object.user.all_antarin_files.filter(folder=antarin_folder_object)
			
			dup_name_flag = 0
			for item in all_user_folders:
				if item.folder_ref.parentfolder==antarin_folder_object and item.folder_ref.name == foldername:
					dup_name_flag = 1
					break
			if dup_name_flag:
				message = api_exceptions.folder_exists()
				return message

		if parentdir:
			print(parentdir)
			value = UploadView.get_parentdir_id(user_object,parentdir,id_val)
			user_folder_object = user_object.user.user_folders.get(pk=int(value))
			antarin_folder_object = user_folder_object.folder_ref

		new_antarin_folder_object = AntarinFolders(user=user_object.user,name=foldername,parentfolder=antarin_folder_object)
		new_antarin_folder_object.save()
		new_user_folder_object = UserFolders(user=user_object.user,folder_ref=new_antarin_folder_object)
		new_user_folder_object.save()

		print(new_antarin_folder_object.pk,new_user_folder_object.pk,new_user_folder_object.folder_ref)

		data = {'id':new_user_folder_object.pk}
		print(data)
		message = {'message':data,'status_code':200}		
		return message

	def post(self,request):
		
		token = self.request.data['token']

		try:
			user_object = Token.objects.get(key = token)
			flag = self.request.data['flag'].strip()
			if flag == 'file':
				argval = self.request.data['argval'].strip() #--filename
				file_object = self.request.data['file']

				if 'newfilename' in self.request.data:
					new_filename = self.request.data['newfilename']
					filename = new_filename
				else:	
					filename = argval

				if ' ' in filename:
					filename = filename.replace(' ','_')
			
				id_val = self.request.data['id']
				return_val = UploadView.add_file(user_object,file_object,filename,id_val)
				message = {'message':return_val}
				if return_val['status_code'] == 200:
					return Response(message,200)
				elif return_val['status_code'] == 400:
					return Response(message,400)
			
			elif flag == 'folder':
				action = self.request.data['action'].strip()
				if action == 'create':
					foldername = self.request.data['foldername']
					parentpath = self.request.data['parentdir']
					id_val = self.request.data['id']
					return_val = UploadView.create_folder(user_object,foldername,parentpath,id_val)
					message = return_val['message']
					if return_val['status_code'] == 200:
						return Response(message,200)
					elif return_val['status_code'] == 400:
						return Response(message,400)
				elif action == 'upload':
					id_val = self.request.data['idval']
					file_object = self.request.data['file']
					filename = self.request.data['argval'].strip()
					if ' ' in filename:
						filename = filename.replace(' ','_')
					return_val = UploadView.add_file_folder(user_object,file_object,filename,id_val)
					message = {'message':return_val}
					if return_val['status_code'] == 200:
						return Response(message,200)
					elif return_val['status_code'] == 400:
						return Response(message,400)
		
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class SeeView(APIView):
	def list_all_spaces(user_object):
		return_val = []
		all_user_projects = user_object.user.user_projects.all()
		#print(all_user_projects)
		for project in all_user_projects:
			if project.status == 'A':
				status = 'Admin'
			else:
				status = 'Contributor'
			return_val.append(project.project.name+"\t"+status+"\t"+str(project.access_key))
		return return_val

	def show_current_directory(user_object,id_val):
		pk = id_val
		return_val = '~antarin'
		if pk != "":
			path_val = []
			string_val = ""
			user_folder_object = user_object.user.user_folders.get(pk=int(pk))
			antarin_folder_object = user_folder_object.folder_ref
			#folder_object = user_object.user.userfolders.get(pk=int(pk))
			while antarin_folder_object.parentfolder is not None:
				path_val.append(antarin_folder_object.name)
				antarin_folder_object = antarin_folder_object.parentfolder
			path_val.append(antarin_folder_object.name)
			for i in range(len(path_val)-1,-1,-1):
				string_val = string_val + "/" + path_val[i]
			
			return_val = return_val + string_val
			return_val = return_val.strip('"')
		return return_val

	def show_project_log(user_object,spacename):
		projectname = spacename
		try:
			project_object = AntarinProjects.objects.get(name=projectname)
			all_logs = AntarinProjectLogs.objects.filter(project=project_object)
			return_val = []
			
			for item in all_logs:
				logs = []
				logs.append(item.timestamp.strftime("[%d/%B/%Y %H:%M:%S]"))
				logs.append(item.action)
				return_val.append(logs)
			
			message = {'message': return_val,'status_code':200}

		except Projects.DoesNotExist:
			message = api_exceptions.project_DoesNotExist()
		
		return message

	def show_clouds(user_object,spacename):
		projectname = spacename
		try:
			project_object = AntarinProjects.objects.get(name=projectname)
			all_clouds = project_object.project_clouds.all()
			ret_val = []
			for item in all_clouds:
				ret_val.append(item.cloud_name+"\t"+item.all_user_clouds.all()[0].user.username+"\t"+str(item.access_key))
				#ret_val[item.instance_name + '[' + item.user.username + ']']= item.access_key
			print(ret_val)
			message = {'message':ret_val,'status_code':200}

		except AntarinProjects.DoesNotExist:
			message = {'message':'Space does not exist.','status_code':404}
		
		return message

	def show_summary(user_object,env,spacename,cloud_id):
		
		if env == 'filesystem':
			user_data = {'firstname':user_object.user.first_name,
						'lastname':user_object.user.last_name,
						'username':user_object.user.username,
						'data_storage_available':user_object.user.userprofile.total_data_storage,
						'data_storage_used':user_object.user.userprofile.data_storage_used
						}
			message = {'message':user_data,'status_code':200}
		
		if env == 'space':
			projectname = spacename
			try:
				project_object = AntarinProjects.objects.get(name=projectname)
				all_userproject_objects = project_object.all_user_projects.all()
				all_projectfiles = project_object.project.all()
				all_projectfolders = project_object.project_ref.all()
				
				contributor_list=[]
				file_list=[]
				folder_list=[]
				admin = ''

				for item in all_userproject_objects:
					contributor_list.append((item.user.first_name+' '+item.user.last_name,item.status))
					if item.status == 'A':
						admin = item.user.first_name + ' '+ item.user.last_name +'('+item.user.username+')'

				for item in all_projectfiles:
					file_list.append((os.path.basename(item.file_ref.file.name),item.file_ref.user.first_name+' '+item.file_ref.user.last_name+'('+item.file_ref.user.username+')'))

				for item in all_projectfolders:
					folder_list.append(('/'+item.folder_ref.name,item.folder_ref.user.first_name+ ' '+item.folder_ref.user.last_name+'('+item.folder_ref.user.username+')'))

				data = {'projectname':projectname,'contributors':contributor_list,'admin':admin,'file_list':file_list,'folder_list':folder_list}
				message = {'message':data,'status_code':200}
			except Projects.DoesNotExist:
				message = api_exceptions.project_DoesNotExist()
		
		if env == 'cloud':
			cloud_id = cloud_id
			#cloud summary
			message = {'message':'cloud summary','status_code':200}

		return message

	def show_files(user_object,env,spacename,cloud_id,dir_id):

		if env == 'filesystem':
			pk = dir_id
			list_val = []
			if pk != "":
				user_folder_object = user_object.user.user_folders.get(pk=int(pk))
				antarin_folder_object = user_folder_object.folder_ref
			else:
				antarin_folder_object = None
			
			for item in user_object.user.user_files.all():
				if item.file_ref.folder == antarin_folder_object:
					list_val.append(os.path.basename(item.file_ref.file.name))
			
			for item in user_object.user.user_folders.all():
				if item.folder_ref.parentfolder == antarin_folder_object:
					list_val.append("/"+item.folder_ref.name)
			
			message = {'message':list_val,'status_code':200}

		if env == 'space':
			try:
				list_val=[]
				projectname = spacename
				project_object = AntarinProjects.objects.get(name=projectname)
				all_projectfiles = project_object.project.all()
				all_projectfolders = project_object.project_ref.all()

				for item in all_projectfiles:
					list_val.append(os.path.basename(item.file_ref.file.name))

				for item in all_projectfolders:
					list_val.append("/"+item.folder_ref.name)
				
				message = {'message':list_val,'status_code':200}

			except Projects.DoesNotExist:
				message = api_exceptions.project_DoesNotExist()

		if env == 'cloud':
			instance_pk = cloud_id
			antarin_cloud_object = AntarinProjectClouds.objects.get(pk=int(instance_pk))
			all_cloud_folders = antarin_cloud_object.cloud_ref.all()

			list_val = []
			for item in all_cloud_folders:
				list_val.append("/" + item.folder_ref.name)

			message = {'message':list_val, 'status_code':200}

		return message

	def post(self,request):
		token = self.request.data['token']
		argument = self.request.data['argument']
		argument = argument.strip()

		try:
			user_object = Token.objects.get(key=token)
			if argument == 'spaces':
				return_val = SeeView.list_all_spaces(user_object)
				message = {'message':return_val}
				return Response(message,status=200)

			if argument == 'path':
				id_val = self.request.data['id']
				return_val = SeeView.show_current_directory(user_object,id_val)
				message = {'message':json.dumps(return_val)}
				return Response(message,status=200)

			if argument == 'log' or argument == 'clouds':
				spacename = self.request.data['spacename'].strip()
				if argument == 'log':
					return_val = SeeView.show_project_log(user_object,spacename)
				if argument == 'clouds':
					return_val = SeeView.show_clouds(user_object,spacename)
				
				message = {'message':return_val['message']}
				
				if return_val['status_code'] == 200:
					return Response(message,status=200)
				elif return_val['status_code'] == 404:
					return Response(message,status=404)

			if argument == 'summary' or argument == 'files':
				env = self.request.data['env'].strip() # env - filesystem/space/cloud
				spacename = self.request.data['spacename'].strip()
				dir_id = self.request.data['id']
				cloud_id = self.request.data['cloud_id']

				if argument == 'summary':	
					return_val = SeeView.show_summary(user_object,env,spacename,cloud_id)
				if argument == 'files':
					return_val = SeeView.show_files(user_object,env,spacename,cloud_id,dir_id)

				message = {'message':return_val['message']}
				
				if return_val['status_code'] == 200:
					return Response(message,status=200)
				elif return_val['status_code'] == 404:
					return Response(message,status=404)


		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)



class EnterView(APIView):

	def enter_folder(user_object,argval,dir_id):
		pk = dir_id
		foldername = argval
		print(foldername)
		print()
		if pk != "":
			user_folder_object = user_object.user.user_folders.get(pk=int(pk))
			antarin_folder_object = user_folder_object.folder_ref
		else:
			if foldername!='..' and foldername!='~antarin':
				try:
					antarin_folder_object = AntarinFolders.objects.get(user=user_object.user,name=foldername,parentfolder=None)
				except AntarinFolders.DoesNotExist:
					message = api_exceptions.folder_DoesNotExist()
					return message
				user_folder_object = antarin_folder_object.all_user_folders.all()[0]
			else:
				antarin_folder_object = None

		if foldername == '..':
			if antarin_folder_object is not None and antarin_folder_object.parentfolder is not None:
				current_directory_object = antarin_folder_object.parentfolder
				current_directory_name = current_directory_object.name
				user_folder_object = UserFolders.objects.get(user=user_object.user,folder_ref=current_directory_object)
				id_val = user_folder_object.pk
			else:
				current_directory_name = "/antarin"
				id_val = ""

			data = {'current_directory':current_directory_name,'id':id_val}
			message = {'message':json.dumps(data),'status_code':200}
		
		elif foldername == '~antarin':
			current_directory = "/antarin"
			id_val = ""
			data = {'current_directory':current_directory,'id':id_val}
			message = {'message':json.dumps(data),'status_code':200}
		
		else:
			if pk == '':
				current_directory = foldername
				id_val = user_folder_object.pk
				data = {'current_directory':current_directory,'id':id_val}
				message = {'message':json.dumps(data),'status_code':200}
			else:
				flag = 0
				all_user_folders = user_object.user.user_folders.all()
				for folder in all_user_folders:
					#print(folder.folder_ref.parentfolder,antarin_folder_object,folder.folder_ref.name,foldername)
					if folder.folder_ref.parentfolder == antarin_folder_object and folder.folder_ref.name == foldername:
						current_directory = folder.folder_ref.name
						user_folder_object = UserFolders.objects.get(user=user_object.user,folder_ref=folder.folder_ref)
						id_val = user_folder_object.pk
						data = {'current_directory':current_directory,'id':id_val}
						flag = 1
						break
				if flag==1:
					message = {'message':json.dumps(data),'status_code':200}
				else:
					message = api_exceptions.folder_DoesNotExist()
		return message

	def enter_project(user_object,spacename,access_key):
		projectid = int(access_key)
		project_flag=0
		all_projects = user_object.user.user_projects.all()
		for project in all_projects:
			if project.access_key == projectid:
				project_flag=1
				data = {'name':project.project.name}
				message = {'message':data,'status_code':200}

		if project_flag==0:
			message = api_exceptions.project_DoesNotExist()
			
		return message

	def enter_cloud(user_object,spacename,access_key):
		projectname = spacename
		instance_access_id = access_key
		try:
			project_object = AntarinProjects.objects.get(name=projectname)
			cloud_object = AntarinProjectClouds.objects.get(access_key=instance_access_id,project=project_object)
			data = {'id':cloud_object.pk,'name':cloud_object.cloud_name}
			message = {'message':data,'status_code':200}
			
		except AntarinProjectClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
		
		return message			

	def post(self,request):
		token = self.request.data['token']
		argument = self.request.data['argument'].strip()
		argval = self.request.data['argval'].strip()
		try:
			user_object = Token.objects.get(key=token)
			if argument == 'folder':
				dir_id = self.request.data['id']
				return_val = EnterView.enter_folder(user_object,argval,dir_id)
				message = {'message':return_val['message']}
				print(message)
				if return_val['status_code'] == 200:
					return Response(message,200)
				elif return_val['status_code'] == 400:
					return Response(message,400)

			if argument == 'space':
				spacename = self.request.data['spacename'].strip()
				return_val = EnterView.enter_project(user_object,spacename,argval)
				message = {'message':return_val['message']}
				if return_val['status_code'] == 200:
					return Response(message,200)
				elif return_val['status_code'] == 404:
					return Response(message,404)

			if argument == 'cloud':
				cloud_id = self.request.data['cloud_id']
				spacename = self.request.data['spacename'].strip()
				return_val = EnterView.enter_cloud(user_object,spacename,argval)
				message = {'message':return_val['message']}
				if return_val['status_code'] == 200:
					return Response(message,200)
				elif return_val['status_code'] == 400:
					return Response(message,400)

		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)


class DeleteView(APIView):

	def remove_all_files_dirs(user_object,all_files,all_folders,pk,foldername):
		
		if pk != "":
			user_folder_object = user_object.user.user_folders.get(pk=int(pk))
			antarin_folder_object = user_folder_object.folder_ref
		else:
			antarin_folder_object = None

		for file in all_files:
			if file.file_ref.folder == antarin_folder_object:
				file.delete()
				print("deleted file "+str(file.file_ref.file.name))
		
		return_list=[]
		for item in all_folders:
			if item.folder_ref.parentfolder == antarin_folder_object:
				return_list.append(item.pk)
				return_list.append(item.folder_ref.name)

		user_folder_object.delete()
		return return_list
	
	def delete_file(user_object,argval,id_val):
		pk = id_val
		name = argval
		file_flag = 0 # 1 - file;0-not a file
		
		return_list=[]
		final_list =[]

		all_user_files = user_object.user.user_files.all()
		all_user_folders = user_object.user.user_folders.all()

		if pk != "":
			user_folder_object = user_object.user.user_folders.get(pk=int(pk))
			antarin_folder_object = user_folder_object.folder_ref
		else:
			antarin_folder_object = None
		
		for item in all_user_files:
			if item.file_ref.folder == antarin_folder_object and os.path.basename(item.file_ref.file.name) == name:
				file_flag = 1
				item.delete()
				message = {'message':"File deleted.",'status_code':200}
				return message

		ref_folder = None
		if file_flag == 0:
			for folder in all_user_folders:
				if folder.folder_ref.parentfolder == antarin_folder_object and folder.folder_ref.name == name:
					ref_folder = folder
					antarin_ref_folder = ref_folder.folder_ref
					break
			if ref_folder is not None:
				folder_empty_flag = 1 # 1 is empty and 0 is non-empty
				for folder in all_user_folders:
					if folder.folder_ref.parentfolder == antarin_ref_folder:
						folder_empty_flag = 0
						break	
				if folder_empty_flag:
					for file in all_user_files:
						if file.file_ref.folder == antarin_ref_folder:
							folder_empty_flag = 0
							break
				if folder_empty_flag:
					ref_folder.delete()
					message = {'message':'Folder deleted.','status_code':200}
					return message
				else:
					#recursive delete
					ref_folder_pk = ref_folder.pk
					ref_folder_name = antarin_ref_folder.name
					return_list = DeleteView.remove_all_files_dirs(user_object,all_user_files,all_user_folders,ref_folder_pk,ref_folder_name)
					if return_list:
						final_list.extend(return_list)
						n = len(return_list)
						i = 0
						while i < n:
							val = DeleteView.remove_all_files_dirs(user_object,all_user_files,all_user_folders,return_list[i],return_list[i+1])
							if val:
								return_list.extend(val)
								final_list.extend(val)
								print(return_list,len(return_list))
							i = i + 2
							n = len(return_list)
					print("\n")
					print ("final_list"+str(final_list))
					
					message = {'message':"Folder deleted.",'status_code':200}
					return message
			else:
				message = api_exceptions.file_DoesNotExist()
				return message

	def delete_project_file(user_object,argval,spacename):
		projectname = spacename
		name = argval

		project_object = AntarinProjects.objects.get(name=projectname)
		project_files = AntarinProjectFiles.objects.filter(project=project_object)

		file_object = None
		found = 0
		is_owner = 0
		for item in project_files: #check if file exists in projectFiles
			if os.path.basename(item.file_ref.file.name) == name:
				file_object = item
				antarin_file_object = item.file_ref
				found = 1
				break

		if found and antarin_file_object.user == user_object.user:
			is_owner = 1
		
		if found and is_owner:
			project_files_object = AntarinProjectFiles.objects.get(project=project_object,file_ref=antarin_file_object)
			project_files_object.delete()

			new_projectlogs_object = AntarinProjectLogs(user=user_object.user,project=project_object,action=user_object.user.username + ' deleted '+ name)
			new_projectlogs_object.save()

			message = {'message':"File removed.",'status_code':200}
			return message

		if found and is_owner == 0:
			message = api_exceptions.permission_denied()
			return message

		if not found:
			project_folders = AntarinProjectFolders.objects.filter(project=project_object)
			folder_object = None
			found = 0
			is_owner = 0
			for item in project_folders: #check if file exists in projectFolders
				if item.folder_ref.name == name:
					antarin_folder_object = item.folder_ref
					found = 1
					break

			if found and antarin_folder_object.user == user_object.user:
				is_owner = 1

			if found == 0:
				message = api_exceptions.file_DoesNotExist()
				return message
			if is_owner == 0:
				message = api_exceptions.permission_denied()
				return message
			if found and is_owner:
				project_folder_object = AntarinProjectFolders.objects.get(project=project_object,folder_ref=antarin_folder_object)
				project_folder_object.delete()
				
				new_projectlogs_object = AntarinProjectLogs(user=user_object.user,project=project_object,action=user_object.user.username + ' deleted '+ name)
				new_projectlogs_object.save()

				message = {'message':"Directory removed.",'status_code':200}
				return message

	def delete_cloud_file(user_object,argval,cloud_id):
		foldername = argval
		cloud_object = AntarinProjectClouds.objects.get(pk=int(cloud_id))

		all_cloud_files = cloud_object.cloud.all()
		all_cloud_folders = cloud_object.cloud_ref.all()
		
		name = argval

		found = 0
		is_owner = 0
		file_object = None
		folder_object = None
		for item in all_cloud_files: 
			if os.path.basename(item.file_ref.file.name) == name:
				file_object = item
				antarin_file_object = item.file_ref
				found = 1
				break

		if found and antarin_file_object.user == user_object.user:
			is_owner = 1
		
		if found and is_owner:
			cloud_file_object = CloudFiles.objects.get(cloud=cloud_object,file_ref=antarin_file_object)
			cloud_file_object.delete()

			message = {'message':"File removed.",'status_code':200}
			return message

		if found and is_owner == 0:
			message = api_exceptions.permission_denied()
			return message

		if not found:
			found = 0
			is_owner = 0
			for item in all_cloud_folders: 
				if item.folder_ref.name == name:
					antarin_folder_object = item.folder_ref
					found = 1
					break

			if found and antarin_folder_object.user == user_object.user:
				is_owner = 1

			if found == 0:
				message = api_exceptions.folder_DoesNotExist()
				return message
			if is_owner == 0:
				message = api_exceptions.permission_denied()
				return message
			if found and is_owner:
				cloud_folder_object = CloudFolders.objects.get(cloud=cloud_object,folder_ref=antarin_folder_object)
				cloud_folder_object.delete()

				message = {'message':"Directory removed.",'status_code':200}
				return message


	def delete_space(user_object,argval,pwd):
		
		projectid = argval
		password = pwd

		username = user_object.user.username
		user_val = User.objects.get(username__exact=username)

		if user_val.check_password(password):
			
			user_project_object = user_object.user.user_projects.get(access_key=projectid)
			project_object = user_project_object.project
			project_object.delete()
			
			message = {'message':'Project deleted.','status_code':200}
		else:
			print('incorrect password')
			message = api_exceptions.incorrect_password()
		return message

	def delete_cloud(user_object,argval,spacename):
		projectname = spacename

		project_object = AntarinProjects.objects.get(name=projectname)
		all_clouds = project_object.project_clouds.all()

		found = False
		has_permissions = False
		for item in all_clouds:
			if item.access_key == int(argval):
				found = True
				break
		
		if found:
			user_cloud_object = item.all_user_clouds.all()[0]
			if user_cloud_object.user.username == user_object.user.username:
				has_permissions = True

		if not found:
			message = api_exceptions.instance_DoesNotExist()
			return message
		if not has_permissions:
			message = api_exceptions.permission_denied()
			return message
		
		cloud_object = item
		cloud_object.delete()
		message = {'message':'Cloud deleted.','status_code':200}
		return message

	def get(self,request):
		token = self.request.data['token']
		projectid = self.request.data['argval'].strip()

		try:
			user_object = Token.objects.get(key=token)
			user_project_object = user_object.user.user_projects.get(access_key=projectid)
			if user_project_object.status != 'A':
				message = api_exceptions.permission_denied()
				return Response(message,status=400)
			else:
				message = {'message':'Has permissions','status_code':200}
				return Response(message,status=200)
		except UserProjects.DoesNotExist:
			message = api_exceptions.project_DoesNotExist()
			return Response(message,status=404)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

	def post(self,request):
		token = self.request.data['token']
		argument = self.request.data['argument'].strip()
		argval = self.request.data['argval'].strip()
		
		try:
			user_object = Token.objects.get(key=token)
			if argument == 'space':
				pwd = self.request.data['pwd']
				return_val = DeleteView.delete_space(user_object,argval,pwd)
				message = {'message':return_val['message']}
				if return_val['status_code'] == 200:
					return Response(message,200)
				elif return_val['status_code'] == 404:
					return Response(message,404)

			if argument == 'cloud':
				spacename = self.request.data['spacename'].strip()
				return_val = DeleteView.delete_cloud(user_object,argval,spacename)
				message = {'message':return_val['message']}
				if return_val['status_code'] == 200:
					return Response(message,200)
				elif return_val['status_code'] == 400:
					return Response(message,400)

			if argument == '-i':
				env = self.request.data['env'].strip()
				if env == 'filesystem':
					id_val = self.request.data['id']
					return_val = DeleteView.delete_file(user_object,argval,id_val)
					
				elif env == 'space':
					spacename = self.request.data['spacename']
					return_val = DeleteView.delete_project_file(user_object,argval,spacename)
					
				elif env == 'cloud':
					cloud_id = self.request.data['cloud_id']
					return_val = DeleteView.delete_cloud_file(user_object,argval,cloud_id)

				message = {'message':return_val['message']}
				if return_val['status_code'] == 200:
					return Response(message,200)
				elif return_val['status_code'] == 400:
					return Response(message,400)

		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)


class AddView(APIView):

	def generate_rand(n):
		llimit = 10**(n-1)
		ulimit = (10**n)-1
		return random.randint(llimit,ulimit)

	def add_contributor(user_object,username,spacename):
		projectname = spacename
		project_object = AntarinProjects.objects.get(name=projectname)
		user_project_object = user_object.user.user_projects.get(project=project_object)
		all_userprojects = UserProjects.objects.all()
		error_flag=0 #0-new contributor object

		if user_project_object.status!='C':
			try:
				contributor_obj = User.objects.get(username=username)
				contributor_project_object = UserProjects.objects.filter(project=project_object,user=contributor_obj)
				
				if not contributor_project_object:
					all_user_projects = contributor_obj.user_projects.all()
					accesskey_list = []
					for item in all_user_projects:
						accesskey_list.append(item.access_key)

					num = AddView.generate_rand(3)
					while num in accesskey_list:
						num = generate_rand(3)

					access_key = num

					new_userprojects_object = UserProjects(user=contributor_obj,project=project_object,status='C',access_key=access_key)
					new_userprojects_object.save()
					
					new_projectlogs_object = AntarinProjectLogs(user=user_object.user,project=project_object,action=user_object.user.username + ' added '+ new_userprojects_object.user.username + ' as contributor.' )
					new_projectlogs_object.save()

					data = {'user':new_userprojects_object.user.username,'acess_key':access_key}
					message = {'message':data,'status_code':200}
					return message
				
				else:
					message = api_exceptions.contributor_exists()
					return message				
			except User.DoesNotExist:
				message = api_exceptions.user_DoesNotExist()
				return message
		else:
			message = api_exceptions.permission_denied()
			return message

	def find_folder(foldername,parentfolder,all_folders):
		folder_flag = 0
		for item in all_folders:
			if item.folder_ref.parentfolder is not None:
				if item.folder_ref.name == foldername and item.folder_ref.parentfolder.parentfolder == parentfolder:
					folder_object = item
					folder_flag = 1
					break
			else:
				if item.folder_ref.name == foldername and item.folder_ref.parentfolder == parentfolder:
					folder_object = item
					folder_flag = 1
					break
		if folder_flag == 0:
			return -1
		return folder_object

	def find_file(filename,parentfolder,all_files):
		file_flag = 0
		for item in all_files:
			#print(item.file_ref.folder,parentfolder.folder_ref,item.file_ref.file.name,filename)
			if item.file_ref.folder == parentfolder.folder_ref and os.path.basename(item.file_ref.file.name) == filename:
				file_object = item
				file_flag = 1
				break
		if file_flag == 0:
			return -1
		return file_object

	def add_to_space(user_object,spacename,item):
		path = item
		projectname = spacename
		project_object = AntarinProjects.objects.get(name=projectname)
		folder_flag = False
		file_flag = False
		path_error = False

		all_folders = user_object.user.user_folders.all()
		error_flag = 0
		plist = path
		plist = plist.split('/')
		if path[0]=='/' and path[-1]=='/':
		    plist = plist[1:-1]
		elif path[0]=='/'and path[-1]!='/':
		    plist = plist[1:]
		elif path[0]!='/' and path[-1]=='/':
		    plist = plist[:-1]
		print (plist)
		parentfolder = None
		if len(plist) == 1:

			val = AddView.find_folder(plist[0],parentfolder,all_folders)
			if val != -1:
				parentfolder = val.folder_ref.parentfolder
				print (parentfolder.name)
			else:
				message = api_exceptions.wrong_path_specified()
				return message
		else:
			for i in range(1,len(plist)):
				val = AddView.find_folder(plist[i],parentfolder,all_folders)
				if val != -1:
					parentfolder = val.folder_ref.parentfolder
					if parentfolder:
						print (parentfolder.name)
				else:
					path_error = True
		
		if not path_error:
			folder_object = val
			all_projectfolders = AntarinProjectFolders.objects.filter(project=project_object)
			for item in all_projectfolders:
				if item.folder_ref == folder_object.folder_ref or item.folder_ref.name == folder_object.folder_ref.name:
					print("Duplicate folder ref")
					error_flag = 1
					break

			if error_flag ==0:
				
				new_projectfolder_object = AntarinProjectFolders(project=project_object,folder_ref=folder_object.folder_ref)
				print("Adding "  + new_projectfolder_object.folder_ref.name + " to " + new_projectfolder_object.project.name)
				new_projectfolder_object.save()

				new_projectlog_object = AntarinProjectLogs(user=user_object.user,project=project_object,action=user_object.user.username + ' added directory '+ new_projectfolder_object.folder_ref.name)
				new_projectlog_object.save()
				folder_flag = True
				message = {'message':'Imported directory.','status_code':200}
				return message
			else:
				message = api_exceptions.folder_exists()
				return message

		if not folder_flag:
			all_folders = user_object.user.user_folders.all()
			all_files = user_object.user.user_files.all()

			plist = path
			plist = plist.split('/')
			if path[0]=='/':
			    plist = plist[1:]
			
			print (plist)
			parentfolder = None
			val = None
			for i in range(1,len(plist)-1):
				print(plist[i],parentfolder)
				val = AddView.find_folder(plist[i],parentfolder,all_folders)
				if val != -1:
					parentfolder = val.folder_ref.parentfolder
					if parentfolder:
						print (parentfolder.name)
				else:
					message = api_exceptions.wrong_path_specified()
					return message
			
			folder_object = val
			file_object = AddView.find_file(plist[-1],folder_object,all_files)
			
			if file_object != -1:
				all_projectfiles = AntarinProjectFiles.objects.filter(project=project_object)
				for item in all_projectfiles:
					if item.file_ref == file_object.file_ref or os.path.basename(item.file_ref.file.name) == os.path.basename(file_object.file_ref.file.name):
						print("duplicate ref")
						error_flag = 1
						break

				if error_flag == 0:
					
					new_projectfile_object = AntarinProjectFiles(project=project_object,file_ref=file_object.file_ref)
					print("Adding " + new_projectfile_object.file_ref.file.name + " to " + new_projectfile_object.project.name)
					new_projectfile_object.save()

					new_projectlogs_object = AntarinProjectLogs(user=user_object.user,project=project_object,action=user_object.user.username + ' added file '+ os.path.basename(new_projectfile_object.file_ref.file.name))
					new_projectlogs_object.save()

					file_flag = True
					message = {'message':'Imported file.','status_code':200}
					return message
				else:
					message = api_exceptions.file_exists()
					return message
		
		if not folder_flag and not file_flag:
			message = api_exceptions.file_DoesNotExist()
			return message


	def add_to_cloud(user_object,argument,spacename,item,cloud_id,packagename):
		projectname = spacename
		instance_id = cloud_id
		section = argument[2:]
		
		project_object = AntarinProjects.objects.get(name=projectname)
		cloud_object = AntarinProjectClouds.objects.get(project=project_object,pk=int(instance_id))	
		if section == 'env':
			project_folder_object = None
			all_project_folders = project_object.project_ref.all()
			for item in all_project_folders:
				if item.folder_ref.name == packagename:
					project_folder_object = item
					antarin_folder_object = item.folder_ref
					break
			if project_folder_object:
				all_cloud_folders = cloud_object.cloud_ref.all()
				for item in all_cloud_folders:
					if item.folder_ref.name == packagename:
						message = api_exceptions.package_exists()
						return message

				new_cloud_folder_object = CloudFolders(cloud=cloud_object,folder_ref=antarin_folder_object)
				new_cloud_folder_object.save()
				message = {'message':'Package added to cloud.','status_code':200}
				return message
			else:
				message=api_exceptions.folder_DoesNotExist()
				return message
		elif section == 'data':
			message = {'message':'Method not implemented.','status_code':200}
			return message
		elif section == 'code':
			message = {'message':'Method not implemented.','status_code':200}
			return message

	def post(self,request):
		token = self.request.data['token']
		argument = self.request.data['argument'].strip()
		try:
			user_object = Token.objects.get(key = token)
			if argument == 'contributor':
				username = self.request.data['argval']
				spacename = self.request.data['spacename']
				return_val = AddView.add_contributor(user_object,username,spacename)
				
			if argument == '-i':
				item = self.request.data['argval']
				spacename = self.request.data['spacename']
				return_val = AddView.add_to_space(user_object,spacename,item)

			if argument[0] == '-' and argument[1] == '-':
				argument = self.request.data['argument']
				item = None
				if 'argval' in self.request.data:
					item = self.request.data['argval']
				spacename = self.request.data['spacename']
				packagename = self.request.data['packagename']
				cloud_id = self.request.data['cloud_id']
				return_val = AddView.add_to_cloud(user_object,argument,spacename,item,cloud_id,packagename)

			message = {'message':return_val}
			if return_val['status_code'] == 200:
				return Response(message,200)
			elif return_val['status_code'] == 400:
				return Response(message,400)

		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class InitializeView(APIView):

	@hosts('localhost')
	def launch_instance(ami,keyname,instance_type,security_group):
		client = boto3.resource('ec2')
		host_list = []
		ids = []	

		start_time = time.time()

		print ('Launching instance..')
		instances = client.create_instances(
			ImageId=ami,
			MinCount=1,
	    	MaxCount=1,
	        KeyName=keyname,
	        InstanceType=instance_type,
	        SecurityGroups=security_group)	
		instance = None
		while 1:
			sys.stdout.flush()
			dns_name = instances[0].public_dns_name
			if dns_name:
				instance = instances[0]
				host_list.append(instance.public_dns_name)
				ids.append(instance.instance_id)
				break
			time.sleep(1.0)
			instances[0].load()
		print ('\nInstance launched.Public DNS:', instance.public_dns_name)
		print ('Connecting to instance.')
		while instance.state['Name'] != 'running':
			print ('.',end='')
			time.sleep(1)
			instance.load()
		print ('Instance in Running state')
		print ('Initializing instance')
		c = boto3.client('ec2')
		while True:
			response = c.describe_instance_status(InstanceIds=ids)
			#print ('.')
			print(time.time()-start_time)
			if response['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status'] == 'passed' and response['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']=='passed':
				break
			time.sleep(1)
		
		#time.sleep(5)
		end_time = time.time()
		elapsed_time  = (end_time - start_time)/60
		print( "ELAPSED TIME = " + str(elapsed_time) + "minutes")
		return host_list,ids

	def setup_instance(key_path,commands): 
		output = []
		try:
			env.user = 'ubuntu'
			env.key_filename = key_path
			for command in commands:
				print(command)
				output.append(run(command))
		finally:
			disconnect_all()
		return output

	def add_files_to_dir(foldername,folderid,commands,parentpath=None):
		if parentpath:
			commands.append('cd '+parentpath+' && mkdir '+foldername)
			print('with cd '+ parentpath)
			print('mkdir ' + foldername)
			parent = parentpath + '/'+foldername
		else:
			commands.append('mkdir '+foldername)
			print('mkdir ' + foldername)
			parent = foldername
		folder_object = AntarinFolders.objects.get(pk=folderid)
		all_files = folder_object.parent_folder_ref.all()
		for item in all_files:
			commands.append('cd '+parent+' && aws s3 cp ' + 's3://antarin-test/media/'+item.file.name+' '+os.path.basename(item.file.name))
			print('with cd '+ parent)
			print('add file '+os.path.basename(item.file.name))

			#&& aws s3 cp '+'s3://antarin-test/media/' + item.projectfile.file_ref.file.name + ' ' + os.path.basename(item.projectfile.file_ref.file.name)
		all_folders_list = AntarinFolders.objects.filter(parentfolder=folder_object)
		all_folders = []
		for item in all_folders_list:
			all_folders.append(item.name)
			all_folders.append(item.pk)
			all_folders.append(parent)
		
		return all_folders,commands

	def post(self,request):
		token = self.request.data['token']
		#print(self.request.data)
		try:
			user_object = Token.objects.get(key = token)
			projectname = self.request.data['spacename']
			
			success = False
			project_object = AntarinProjects.objects.get(name=projectname)
			accesskey = None
			if 'argval' in self.request.data:
				accesskey = self.request.data['argval'] 
			if accesskey:
				cloud_object = project_object.project_clouds.get(access_key=int(accesskey))
			else:
				cloud_id = self.request.data['cloud_id']
				cloud_object = AntarinProjectClouds.objects.get(project=project_object,pk=int(cloud_id))	

			all_cloud_packages = cloud_object.cloud_ref.all()
			cloud_package_object = None

			packages = json.loads(self.request.data['packages'])
			
			print(packages)
			if cloud_object.is_active == False:
				#launch instance
				sec_group = []
				sec_group.append(cloud_object.security_group)
				key_name = 'ec2test'

				res = execute(InitializeView.launch_instance,cloud_object.ami_id,key_name,cloud_object.instance_type,sec_group)
				print (res['localhost'][0])

				if res['localhost'][0]:
					dns_name = res['localhost'][0][0]
					instance_id_val = res['localhost'][1][0]
					cloud_object.dns_name = res['localhost'][0][0]
					cloud_object.instance_id = instance_id_val
					cloud_object.is_active = True
					cloud_object.save()
					success=True

					for package in packages:
						packagename = package

						for item in all_cloud_packages:
							if item.folder_ref.name == packagename:
								cloud_package_object = item
								break
						
						if cloud_package_object:							
							folder_object = cloud_package_object.folder_ref
							folder_name = folder_object.name
							folder_id = folder_object.pk
							commands = []
							value = InitializeView.add_files_to_dir(folder_name,folder_id,commands)
							all_folders = value[0]
							final_list = []
							commands = value[1]
							if all_folders:
								n = len(all_folders)
								i = 0
								final_list.extend(all_folders)
								while i<n:
									val = InitializeView.add_files_to_dir(all_folders[i],all_folders[i+1],commands,all_folders[i+2])
									if val:
										all_folders.extend(val[0])
										final_list.extend(val[0])
										commands = val[1]
										#print(all_folders,final_list)
									i += 3
									n = len(all_folders)
							for command in commands:
								print(command)
							#commands.append('sudo apt-get build-dep python-matplotlib')
							commands.append('cd ' + packagename +' && sudo pip install -r requirements.txt')
							output = execute(InitializeView.setup_instance,key_path,commands,hosts = cloud_object.dns_name)
							#output_text = output[instance_object.dns_name[0]]
							print(output)
						else:
							message = api_exceptions.package_DoesNotExist(packagename)
							return Response(message,status=400)
					
					message = {'message': 'Cloud initilization successful.','status_code':200}
					return Response(message,status=200)
				
				else:
					message = api_exceptions.intance_launch_error()
					return Response(message,status=400)
			else:
				message = {'message': 'Instance in running state','status_code':200}
				return Response(message,status=200)

		except AntarinProjectClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)

		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class RunView(APIView):

	def setup_instance(key_path,commands): 
		env.warn_only = True
		output = []
		try:
			env.user = 'ubuntu'
			env.key_filename = key_path
			for command in commands:
				print(command)
				value = run(command)
				if value.stderr != "":
					output_text = "Error while executing command %s : %s" %(command, value.stderr)
					break
				output.append(run(command))
		finally:
			print("disconenct worked")
			disconnect_all()
		return output

	def post(self,request):
		token = self.request.data['token']
		#print(self.request.data)
		try:
			user_object = Token.objects.get(key = token)
			projectname = self.request.data['spacename']
			packagename = self.request.data['packagename']
			shell_command = self.request.data['shell_command']
			commands = []

			data_flag = False
			requirements_flag = False
			
			project_object = AntarinProjects.objects.get(name=projectname)
			accesskey = None
			if 'argval' in self.request.data:
				accesskey = self.request.data['argval'] 
			if accesskey:
				cloud_object = project_object.project_clouds.get(access_key=int(accesskey))
			else:
				cloud_id = self.request.data['cloud_id']
				cloud_object = AntarinProjectClouds.objects.get(project=project_object,pk=int(cloud_id))	

			all_cloud_packages = cloud_object.cloud_ref.all()
			cloud_package_object = None

			print('dns name = '+ str(cloud_object.dns_name))
			print('\n')

			for item in all_cloud_packages:
				print(item.folder_ref.name,packagename)
				if item.folder_ref.name == packagename:
					cloud_package_object = item
					break
			if cloud_package_object:
				package_folder = cloud_package_object.folder_ref
				folders = package_folder.parent_folder_reference.all()
				files = package_folder.parent_folder_ref.all()
				for item in folders:
					if item.name == 'data':
						data_flag = True
						break
				for item in files:
					if os.path.basename(item.file.name) == 'requirements.txt':
						requirements_flag = True
						break

				if data_flag == False:
					message = api_exceptions.no_data_folder()
					return Response(message,status=400)

				if requirements_flag == False:
					message = api_exceptions.no_requirements_file()
					return Response(message,status=400)

				if cloud_object.is_active == True:
					commands.append(shell_command)
					#host = list(instance_object.dns_name)
					output = execute(RunView.setup_instance,key_path,commands,hosts = cloud_object.dns_name)
					print(output)
					output_text = output[cloud_object.dns_name]
					for item in output_text:
						print(item)
					message = {'message': output_text,'status_code':200}
					return Response(message,status=200)
				else:
					message = api_exceptions.cloud_notRunning()
					return Response(message,status=400)
			else:
				message = api_exceptions.package_DoesNotExist()
				return Response(message,status=400)
		except SystemExit:
			message = "error"
			return Response(message,status=400)
		except AntarinProjectClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class SleepView(APIView):

	def post(self,request):
		token = self.request.data['token']
		try:
			user_object = Token.objects.get(key = token)
			projectname = self.request.data['spacename']
			project_object = AntarinProjects.objects.get(name=projectname)
			accesskey = None
			if 'argval' in self.request.data:
				accesskey = self.request.data['argval'] 
			if accesskey:
				cloud_object = project_object.project_clouds.get(access_key=int(accesskey))
			else:
				cloud_id = self.request.data['cloud_id']
				cloud_object = AntarinProjectClouds.objects.get(project=project_object,pk=int(cloud_id))

			if cloud_object.is_active == True:
				cloud_id = []
				cloud_id.append(cloud_object.instance_id)
				client = boto3.client('ec2')
				response = client.stop_instances(InstanceIds=cloud_id)
				cloud_object.is_active = False
				cloud_object.save()
				print (response)
				message = {'message':'Cloud stopped.','status_code':200}
				return Response(message,status=200)
			else:
				message = api_exceptions.instance_not_running()
				return Response(message,status=400)
		except AntarinProjectClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)


class CloneView(APIView):

	def clone_all(folder_object,user_object,root,parentfolder=None):
		print("cloning folder "+folder_object.name)
		
		all_files = AntarinFiles.objects.filter(folder=folder_object)
		all_folders = AntarinFolders.objects.filter(parentfolder=folder_object)
		
		cloned_folder = folder_object
		cloned_folder.pk = None
		cloned_folder.user = user_object.user
		cloned_folder.name = folder_object.name
		if root:
			cloned_folder.parentfolder = None
		else:
			cloned_folder.parentfolder = parentfolder
		cloned_folder.save()

		for item in all_files:
			print("cloning file "+ item.file.name)
			cloned_file = item
			cloned_file.file.name = item.file.name			
			cloned_file.folder = cloned_folder
			cloned_file.pk = None
			cloned_file.user = user_object.user
			cloned_file.save()

		for item in all_folders:
			CloneView.clone_all(item,user_object,False,cloned_folder)

		return cloned_folder

	def generate_rand(n):
		llimit = 10**(n-1)
		ulimit = (10**n)-1
		return random.randint(llimit,ulimit)

	def post(self,request):
		token = self.request.data['token']
		try:
			user_object = Token.objects.get(key = token)
			accesskey = self.request.data['argval']
			projectname = self.request.data['spacename']
			project_object = AntarinProjects.objects.get(name=projectname)
			
			cloud_object = project_object.project_clouds.get(access_key=int(accesskey))
			all_project_clouds = project_object.project_clouds.all()

			accesskey_list = []
			for item in all_project_clouds:
				accesskey_list.append(item.access_key)

			access_key_length = 3
			num = CloneView.generate_rand(access_key_length)
			while num in accesskey_list:
				num = CloneView.generate_rand(access_key_length)

			access_key = num

			all_cloud_folders = cloud_object.cloud_ref.all()
			
			cloned_object = cloud_object
			cloned_object.access_key = num
			cloned_object.cloud_name = cloud_object.cloud_name + '(cloned)'
			cloned_object.pk = None
			cloned_object.instance_id = ''
			cloned_object.dns_name = ''
			cloned_object.is_active = False
			cloned_object.project = cloud_object.project
			cloned_object.save()

			new_user_cloud_object = UserClouds(cloud=cloned_object,user=user_object.user)
			new_user_cloud_object.save()


			for item in all_cloud_folders:
				print("cloning package "+item.folder_ref.name)
				folder_object = CloneView.clone_all(item.folder_ref,user_object,True)
				new_cloned_package = CloudFolders(cloud=cloned_object,folder_ref=folder_object)
				new_cloned_package.save() 
			
			message = {'message': cloned_object.access_key,'status_code':200}
			return Response(message,status=200)

		except AntarinProjectClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class MergeView(APIView):

	def clone_all(folder_object,user_object,root,parentfolder=None):
		print("cloning folder "+folder_object.name)
		
		all_files = AntarinFiles.objects.filter(folder=folder_object)
		all_folders = AntarinFolders.objects.filter(parentfolder=folder_object)
		
		cloned_folder = folder_object
		cloned_folder.pk = None
		cloned_folder.user = user_object.user
		cloned_folder.name = folder_object.name
		if root:
			cloned_folder.parentfolder = None
		else:
			cloned_folder.parentfolder = parentfolder
		cloned_folder.save()

		for item in all_files:
			print("cloning file "+ item.file.name)
			cloned_file = item
			cloned_file.file.name = item.file.name			
			cloned_file.folder = cloned_folder
			cloned_file.pk = None
			cloned_file.user = user_object.user
			cloned_file.save()

		for item in all_folders:
			CloneView.clone_all(item,user_object,False,cloned_folder)

		return cloned_folder

	def post(self,request):
		token = self.request.data['token']
		try:
			user_object = Token.objects.get(key = token)
			projectname = self.request.data['spacename']
			
			project_object = AntarinProjects.objects.get(name=projectname)
			
			source_access_key = self.request.data['source_id']
			destination_access_key = self.request.data['destination_id']
			
			source_instance_object = project_object.project_clouds.get(access_key=int(source_access_key))
			destination_instance_object = project_object.project_clouds.get(access_key=int(destination_access_key))

			all_source_instance_packages = source_instance_object.cloud_ref.all()
			all_destination_instance_packages = destination_instance_object.cloud_ref.all()

			destination_package_names = [i.folder_ref.name for i in all_destination_instance_packages]
			print(destination_package_names)
			
			for package_object in all_source_instance_packages:
				print(package_object.folder_ref.name)
				temp = str(package_object.folder_ref.name)
				foldername = package_object.folder_ref.name
				if package_object.folder_ref.name in destination_package_names:
					foldername = temp + "_copy"

				folder_object = MergeView.clone_all(package_object.folder_ref,user_object,True)
				new_destination_package_object = CloudFolders(cloud=destination_instance_object,folder_ref=folder_object)
				new_destination_package_object.folder_ref.name = foldername
				new_destination_package_object.save()
				print(package_object.folder_ref.name,new_destination_package_object.folder_ref.name)

			message = {'message': 'Merge successful','status_code':200}
			return Response(message,status=200)

		except AntarinProjectClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)
