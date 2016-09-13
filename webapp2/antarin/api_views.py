import hashlib,random,json,boto,os
import boto3,sys,time,copy
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
from django.db import IntegrityError

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
			folder_object = user_object.user.user_folders.get(pk=int(pk))
		else:
			folder_object = None

		dup_name_flag = False
		all_folders_inside_currdir = user_object.user.user_folders.filter(parentfolder=folder_object)
		for  item in all_folders_inside_currdir:
			if item.foldername == foldername:
				dup_name_flag = True
				break
		if dup_name_flag:
			message = api_exceptions.folder_exists()
			return message
		
		new_folder_object = UserFolders(user=user_object.user,foldername=foldername,parentfolder=folder_object)
		new_folder_object.save()
		
		data = {'id':new_folder_object.pk}
		message = {'message':json.dumps(data),'status_code':200}	
		print(message)	
		return message

	def new_project(user_object,argval):
		spacename = argval
		try:
			spacename = user_object.user.username + ':' + spacename
			
			#create project object
			new_space_object = AntarinSpaces(name=spacename)
			new_space_object.save()
			
			#generate accesskey
			all_user_spaces = user_object.user.user_spaces.all()
			accesskey_list = []
			for item in all_user_spaces:
				accesskey_list.append(item.access_key)

			num = NewView.generate_rand(3)
			while num in accesskey_list:
				num = NewView.generate_rand(3)

			access_key = num

			#create userprojects object
			new_userspaces_object = UserSpaces(user=user_object.user,space=new_space_object,status='A',access_key=access_key)
			new_userspaces_object.save()
			
			#add to logs
			new_spacelog_object = AntarinSpaceLogs(user=user_object.user,space=new_space_object,action=user_object.user.username + ' created '+ spacename)
			new_spacelog_object.save()
			
			data = {'spacename':new_space_object.name,'access_key':access_key}
			message = {'message':data,'status_code':200}
			return message
		
		except IntegrityError:
			message = api_exceptions.project_exists()
			return message
		
	def new_cloud(user_object,spacename,argval,ami_id,instance_type,region):
		instance_name = argval

		space_object = AntarinSpaces.objects.get(name=spacename)
		all_space_clouds = space_object.space_clouds.all()
		
		dup_name_flag = False
		for  item in all_space_clouds:
			if item.cloud_name == instance_name:
				dup_name_flag = True
				break
				print("duplicate names")
		
		if dup_name_flag:
			message = api_exceptions.instance_exists()
			return message

		accesskey_list = []
		for item in all_space_clouds:
			accesskey_list.append(item.access_key)

		num = NewView.generate_rand(3)
		while num in accesskey_list:
			num = generate_rand(3)

		access_key = num
		print(access_key)

		new_cloud_object = AntarinClouds(user=user_object.user,space=space_object,cloud_name=instance_name,ami_id=ami_id,region=region,instance_type=instance_type,access_key=access_key)
		new_cloud_object.save()

		new_spacelogs_object = AntarinSpaceLogs(user=user_object.user,space=space_object,action=user_object.user.username + ' created cloud '+ new_cloud_object.cloud_name)
		new_spacelogs_object.save()

		data = {'access_key':new_cloud_object.access_key}
		message={'message':data,'status_code':200}
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
		total_val = 0
		for file in all_files:
			total_val = total_val + file.file_ref.file.size
		return size(total_val)

	def add_file(user_object,file_object,filename,id_val):

		pk = id_val

		filename = os.path.basename(filename)

		if pk!="":
			folder_object = user_object.user.user_folders.get(pk=int(pk))
		else:
			folder_object = None

		all_files_in_currdir = user_object.user.user_files.filter(parentfolder=folder_object)
		
		dup_name_flag = False
		for item in all_files_in_currdir:
			if os.path.basename(item.file_ref.file.file.name) == filename:
				dup_name_flag = True
				break

		if dup_name_flag:
			message = api_exceptions.file_exists()
			return message

		antarin_file_object = AntarinFiles(file=file_object)
		antarin_file_object.save()

		user_files_object = UserFiles(user=user_object.user,file_ref=antarin_file_object,parentfolder=folder_object)
		user_files_object.save()
		
		all_files = user_object.user.user_files.all()
		used_data_storage = UploadView.calculate_used_data_storage(all_files)
		user_object.user.userprofile.data_storage_used = str(used_data_storage)
		user_object.user.save()
		user_object.user.userprofile.save()
		
		#catch error when save didn't work fine and return status 400
		print("\n")
		message = {'message':"File upload successful.",'status_code':200}
		return message

	def add_file_folder(user_object,file_object,filename,id_val):
		
		pk = id_val
		
		filename = os.path.basename(filename)

		if pk!="":
			folder_object = user_object.user.user_folders.get(pk=int(pk))
		else:
			folder_object = None

		antarin_file_object = AntarinFiles(file=file_object)
		antarin_file_object.save()

		user_files_object = UserFiles(user=user_object.user,file_ref=antarin_file_object,parentfolder=folder_object)
		user_files_object.save()
		
		all_files = user_object.user.user_files.all()
		used_data_storage = UploadView.calculate_used_data_storage(all_files)
		user_object.user.userprofile.data_storage_used = str(used_data_storage)
		user_object.user.save()
		user_object.user.userprofile.save()
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
				folder_object = user_object.user.user_folders.get(pk=id_val)
				next_folder_object = folder_object.all_folders.get(foldername=item)
				id_val = next_folder_object.pk
		else:
			print("here")
			folder_object = user_object.user.user_folders.get(foldername=l[0],parentfolder=None)
			id_val = folder_object.pk
			for item in l[1:]:
				next_folder_object = folder_object.all_folders.get(foldername=item)
				id_val = next_folder_object.pk
				folder_object = user_object.user.user_folders.get(pk=id_val)

		return str(id_val)

	def create_folder(user_object,foldername,parentdir,id_val):
		pk = id_val

		if not parentdir:
			if pk != "":
				folder_object = user_object.user.user_folders.get(pk=int(pk))
			else:
				folder_object = None

			dup_name_flag = False
			all_folders_inside_currdir = user_object.user.user_folders.filter(parentfolder=folder_object)
			for  item in all_folders_inside_currdir:
				if item.foldername == foldername:
					dup_name_flag = True
					break
					print("duplicate names")
			
			if dup_name_flag:
				message = api_exceptions.folder_exists()
				return message

		if parentdir:
			print(parentdir)
			value = UploadView.get_parentdir_id(user_object,parentdir,id_val)
			print('value = '+value)
			folder_object = user_object.user.user_folders.get(pk=int(value))

		new_folder_object = UserFolders(user=user_object.user,foldername=foldername,parentfolder=folder_object)
		new_folder_object.save()
		
		data = {'id':new_folder_object.pk}
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
		all_user_spaces = user_object.user.user_spaces.all()
		for space in all_user_spaces:
			if space.status == 'A':
				status = 'Admin'
			else:
				status = 'Contributor'
			return_val.append(space.space.name+"\t"+status+"\t"+str(space.access_key))
		return return_val

	def show_current_directory(user_object,id_val,env,spacename,cloud_id,spacedir_id,clouddir_id):
		if env == 'filesystem':
			pk = id_val
			return_val = '~antarin'
			
			if pk != "":
				path_val = []
				string_val = ""
				folder_object = user_object.user.user_folders.get(pk=int(pk))
				
				while folder_object.parentfolder is not None:
					path_val.append(folder_object.foldername)
					folder_object = folder_object.parentfolder
				
				path_val.append(folder_object.foldername)
				
				for i in range(len(path_val)-1,-1,-1):
					string_val = string_val + "/" + path_val[i]
				
				return_val = return_val + string_val
				return_val = return_val.strip('"')
		
		if env == 'space':
			pk = spacedir_id
			return_val = '~space'

			space_object = AntarinSpaces.objects.get(name=spacename)

			if pk != "":
				path_val = []
				string_val = ""
				folder_object = space_object.space_folders.get(pk=int(pk))
				
				while folder_object.parentfolder is not None:
					path_val.append(folder_object.foldername)
					folder_object = folder_object.parentfolder
				
				path_val.append(folder_object.foldername)
				
				for i in range(len(path_val)-1,-1,-1):
					string_val = string_val + "/" + path_val[i]
				
				return_val = return_val + string_val
				return_val = return_val.strip('"')


		if env == 'cloud':
			pk = clouddir_id
			return_val = '~cloud'

			cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))

			if pk != "":
				path_val = []
				string_val = ""
				folder_object = cloud_object.cloud_folders.get(pk=int(pk))
				
				while folder_object.parentfolder is not None:
					path_val.append(folder_object.foldername)
					folder_object = folder_object.parentfolder
				
				path_val.append(folder_object.foldername)
				
				for i in range(len(path_val)-1,-1,-1):
					string_val = string_val + "/" + path_val[i]
				
				return_val = return_val + string_val
				return_val = return_val.strip('"')

		return return_val

	def show_project_log(user_object,spacename):
		try:
			space_object = AntarinSpaces.objects.get(name=spacename)
			all_log = AntarinSpaceLogs.objects.filter(space=space_object)
			return_val = []
			
			for item in all_log:
				logs = []
				logs.append(item.timestamp.strftime("[%d/%B/%Y %H:%M:%S]"))
				logs.append(item.action)
				return_val.append(logs)
			
			message = {'message': return_val,'status_code':200}

		except AntarinSpaces.DoesNotExist:
			message = api_exceptions.project_DoesNotExist()
		
		return message

	def show_clouds(user_object,spacename):
		
		try:
			space_object = AntarinSpaces.objects.get(name=spacename)
			all_clouds = space_object.space_clouds.all()
			ret_val = []
			
			for item in all_clouds:
				ret_val.append(item.cloud_name+"\t"+item.user.username+"\t"+str(item.access_key))
			
			message = {'message':ret_val,'status_code':200}

		except AntarinSpaces.DoesNotExist:
			message = api_exceptions.project_DoesNotExist()
		
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
			
			try:
				space_object = AntarinSpaces.objects.get(name=spacename)
				all_userspace_objects = space_object.all_user_spaces.all()
				all_spacefiles = space_object.space_files.filter(parentfolder=None)
				all_spacefolders = space_object.space_folders.filter(parentfolder=None)
				
				contributor_list=[]
				file_list=[]
				folder_list=[]
				admin = ''

				for item in all_userspace_objects:
					contributor_list.append((item.user.first_name+' '+item.user.last_name,item.status))
					if item.status == 'A':
						admin = item.user.first_name + ' '+ item.user.last_name +'('+item.user.username+')'

				for item in all_spacefiles:
					file_list.append((os.path.basename(item.file_ref.file.name),item.added_by.first_name+' '+item.added_by.last_name+'('+item.added_by.username.lower()+')'))
					

				for item in all_spacefolders:
					folder_list.append(('/'+item.foldername,item.added_by.first_name+' '+item.added_by.last_name+'('+item.added_by.username.lower()+')'))

				data = {'projectname':spacename,'contributors':contributor_list,'admin':admin,'file_list':file_list,'folder_list':folder_list}
				message = {'message':data,'status_code':200}
			except AntarinSpaces.DoesNotExist:
				message = api_exceptions.project_DoesNotExist()
		
		if env == 'cloud':
			cloud_id = cloud_id
			#cloud summary
			message = {'message':'cloud summary','status_code':200}

		return message

	def show_files(user_object,env,spacename,cloud_id,dir_id,spacedir_id,clouddir_id):

		if env == 'filesystem':
			pk = dir_id
			list_val = []

			if pk != "":
				folder_object = user_object.user.user_folders.get(pk=int(pk))
			else:
				folder_object = None
			
			all_files = user_object.user.user_files.filter(parentfolder=folder_object)
			all_folders = user_object.user.user_folders.filter(parentfolder=folder_object)

			for item in all_files:
				list_val.append(os.path.basename(item.file_ref.file.name))
			
			for item in all_folders:
				list_val.append("/"+item.foldername)
			
			message = {'message':list_val,'status_code':200}

		if env == 'space':
			try:
				list_val=[]
				space_object = AntarinSpaces.objects.get(name=spacename)
				if spacedir_id != '':
					folder_object = AntarinSpaceFolders.objects.get(pk=int(spacedir_id))
				else:
					folder_object = None
				
				all_spacefiles = space_object.space_files.filter(parentfolder=folder_object)
				all_spacefolders = space_object.space_folders.filter(parentfolder=folder_object)
				
				for item in all_spacefiles:
					list_val.append(os.path.basename(item.file_ref.file.name))

				for item in all_spacefolders:
					list_val.append("/"+item.foldername)

				message = {'message':list_val,'status_code':200}

			except AntarinSpaces.DoesNotExist:
				message = api_exceptions.project_DoesNotExist()

		if env == 'cloud':
			list_val = []
			cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))

			if clouddir_id  != '':
				folder_object = AntarinCloudFolders.objects.get(pk=int(clouddir_id))
			else:
				folder_object = None

			all_cloud_files = cloud_object.cloud_files.filter(parentfolder=folder_object)
			all_cloud_folders = cloud_object.cloud_folders.filter(parentfolder=folder_object)
			
			for item in all_cloud_folders:
				list_val.append("/"+item.foldername)
				
			for item in all_cloud_files:
				list_val.append(os.path.basename(item.file_ref.file.name))

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
				env = self.request.data['env'].strip()
				spacename = self.request.data['spacename'].strip()
				cloud_id = self.request.data['cloud_id']
				spacedir_id = self.request.data['spacedir_id']
				clouddir_id = self.request.data['clouddir_id']
				return_val = SeeView.show_current_directory(user_object,id_val,env,spacename,cloud_id,spacedir_id,clouddir_id)
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
					spacedir_id = self.request.data['spacedir_id']
					clouddir_id = self.request.data['clouddir_id']
					return_val = SeeView.show_files(user_object,env,spacename,cloud_id,dir_id,spacedir_id,clouddir_id)

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

		if pk != "":
			folder_object = user_object.user.user_folders.get(pk=int(pk))
		else:
			folder_object = None

		if foldername == '..':
			if folder_object is not None and folder_object.parentfolder is not None:
				current_directory = folder_object.parentfolder.foldername
				id_val = folder_object.parentfolder.pk
			else:
				current_directory = "/antarin"
				id_val = ""
			data = {'current_directory':current_directory,'id':id_val}
			message = {'message':json.dumps(data),'status_code':200}
		
		elif foldername == '~antarin':
			current_directory = "/antarin"
			id_val = ""
			data = {'current_directory':current_directory,'id':id_val}
			message = {'message':json.dumps(data),'status_code':200}
		
		else:
			flag = False
			all_folders = user_object.user.user_folders.all()
			for folder in all_folders:
				if folder.parentfolder == folder_object and folder.foldername == foldername:
					current_directory = folder.foldername
					id_val = folder.pk
					data = {'current_directory':current_directory,'id':id_val}
					flag = True
					break
			if flag:
				message = {'message':json.dumps(data),'status_code':200}
			else:
				message = api_exceptions.folder_DoesNotExist()
		
		return message

	def enter_folder_space(user_object,argval,spacedir_id,spacename):

		pk = spacedir_id
		foldername = argval
		space_object = AntarinSpaces.objects.get(name=spacename)

		if pk != "":
			folder_object = space_object.space_folders.get(pk=int(pk))
		else:
			folder_object = None
		
		if foldername == '..':
			if folder_object is not None and folder_object.parentfolder is not None:
				id_val = folder_object.parentfolder.pk
			else:
				id_val = ""
			data = {'dir_val':id_val}
			message = {'message':json.dumps(data),'status_code':200}
		
		elif foldername == '~space':
			id_val = ""
			data = {'dir_val':id_val}
			message = {'message':json.dumps(data),'status_code':200}
		
		else:
			try:
				return_folder_object = space_object.space_folders.get(parentfolder=folder_object,foldername=foldername)
				id_val = return_folder_object.pk
				data = {'dir_val':id_val}
				message = {'message':json.dumps(data),'status_code':200}
			except AntarinSpaceFolders.DoesNotExist:
				message = api_exceptions.folder_DoesNotExist()
		return message

	def enter_folder_cloud(user_object,argval,clouddir_id,spacename,cloud_id):


		pk = clouddir_id
		foldername = argval
		cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))

		if pk != "":
			folder_object = cloud_object.cloud_folders.get(pk=int(pk))
		else:
			folder_object = None
		
		if foldername == '..':
			if folder_object is not None and folder_object.parentfolder is not None:
				id_val = folder_object.parentfolder.pk
			else:
				id_val = ""
			data = {'dir_val':id_val}
			message = {'message':json.dumps(data),'status_code':200}
		
		elif foldername == '~cloud':
			id_val = ""
			data = {'dir_val':id_val}
			message = {'message':json.dumps(data),'status_code':200}
		
		else:
			try:
				return_folder_object = cloud_object.cloud_folders.get(parentfolder=folder_object,foldername=foldername)
				id_val = return_folder_object.pk
				data = {'dir_val':id_val}
				message = {'message':json.dumps(data),'status_code':200}
			except AntarinCloudFolders.DoesNotExist:
				message = api_exceptions.folder_DoesNotExist()
		return message

	def enter_project(user_object,spacename,access_key):
		try:
			user_space_object = user_object.user.user_spaces.get(access_key=int(access_key))
			data = {'name':user_space_object.space.name}
			message = {'message':data,'status_code':200}

		except UserSpaces.DoesNotExist:
			message = api_exceptions.project_DoesNotExist()
			
		return message

	def enter_cloud(user_object,spacename,access_key):
		
		try:
			space_object = AntarinSpaces.objects.get(name=spacename)
			cloud_object = AntarinClouds.objects.get(access_key=access_key,space=space_object)
			
			data = {'id':cloud_object.pk,'name':cloud_object.cloud_name}
			message = {'message':data,'status_code':200}
			
		except AntarinClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
		
		return message			

	def post(self,request):
		token = self.request.data['token']
		argument = self.request.data['argument'].strip()
		argval = self.request.data['argval'].strip()
		env = self.request.data['env'].strip()
		try:
			user_object = Token.objects.get(key=token)
			if argument == 'folder':
				if env == 'filesystem':
					dir_id = self.request.data['id']
					return_val = EnterView.enter_folder(user_object,argval,dir_id)
				if env == 'space':
					spacedir_id = self.request.data['spacedir_id']
					spacename = self.request.data['spacename'].strip()
					return_val = EnterView.enter_folder_space(user_object,argval,spacedir_id,spacename)
				if env == 'cloud':
					clouddir_id = self.request.data['clouddir_id']
					cloud_id = self.request.data['cloud_id']
					spacename = self.request.data['spacename'].strip()
					return_val = EnterView.enter_folder_cloud(user_object,argval,clouddir_id,spacename,cloud_id)
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
	
		if pk!='':
			folder_object = user_object.user.user_folders.get(pk=int(pk))
		else:
			folder_object = None

		print ("folder object = "+str(folder_object))
		
		for file in all_files:
			if file.parentfolder == folder_object:
				file.delete()
				print("deleted file "+str(file.file_ref.file.name))
		
		return_list=[]
		for item in all_folders:
			if item.parentfolder == folder_object:
				return_list.append(item.pk)
				return_list.append(item.foldername)

		return return_list

	def delete_file(user_object,argval,id_val):

		pk = id_val
		name = argval
		file_flag = False # true - file;false-not a file
		ref_fodler=None
		return_list=[]
		final_list =[]

		all_files = user_object.user.user_files.all()
		all_folders = user_object.user.user_folders.all()

		if pk!='':
			folder_object = user_object.user.user_folders.get(pk=int(pk))
		else:
			folder_object = None


		for file in user_object.user.user_files.filter(parentfolder=folder_object):
			if os.path.basename(file.file_ref.file.name) == name:
				file_flag = True
				file.delete()
				message = {'message':"File deleted.",'status_code':200}
				return message

		ref_folder = None
		if file_flag == False:
			for folder in user_object.user.user_folders.filter(parentfolder=folder_object):
				if folder.foldername == name:
					ref_folder = folder
					break
			
			if ref_folder is not None:
				folder_empty_flag = True # True is empty and False is non-empty
				for folder in all_folders:
					if folder.parentfolder == ref_folder:
						folder_empty_flag = False
						break

				if folder_empty_flag:
					for file in all_files:
						if file.parentfolder == ref_folder:
							folder_empty_flag = False
							break

				if folder_empty_flag:
					ref_folder.delete()
					message = {'message':'Folder deleted.','status_code':200}
					return message

				else:
					#recursive delete
					ref_folder_pk = ref_folder.pk
					ref_folder_name = ref_folder.foldername
					return_list = DeleteView.remove_all_files_dirs(user_object,all_files,all_folders,ref_folder_pk,ref_folder_name)
					if return_list:
						#print(return_list)
						final_list.extend(return_list)
						n = len(return_list)
						i = 0
						while i < n:
						#for i in range(0,len(return_list),2):
							val = DeleteView.remove_all_files_dirs(user_object,all_files,all_folders,return_list[i],return_list[i+1])
							if val:
								return_list.extend(val)
								final_list.extend(val)
								print(return_list,len(return_list))
							i = i + 2
							n = len(return_list)
					print("\n")
					print ("final_list"+str(final_list))
					
					folder_object = user_object.user.user_folders.get(pk=int(ref_folder_pk))
					print("deleting folder  " + ref_folder_name+ "   "+str(ref_folder_pk))
					folder_object.delete()
					message = {'message':"Folder deleted.",'status_code':200}
					return message				
						
			else:
				message = api_exceptions.file_DoesNotExist()
				return message

	def remove_all_files_dirs_space(user_object,spacename,all_files,all_folders,pk,foldername):
	
		space_object = AntarinSpaces.objects.get(name=spacename)

		if pk!='':
			folder_object = space_object.space_folders.get(pk=int(pk))
		else:
			folder_object = None

		print ("folder object = "+str(folder_object))
		
		for file in all_files:
			if file.parentfolder == folder_object:
				if file.added_by.username == user_object.user.username:
					file.delete()
					print("deleted file "+str(file.file_ref.file.name))
				else:
					message = api_exceptions.permission_denied()
					return message
				
		
		return_list=[]
		for item in all_folders:
			if item.parentfolder == folder_object:
				return_list.append(item.pk)
				return_list.append(item.foldername)

		return return_list

	def delete_project_file(user_object,argval,spacename,spacedir_id):

		pk = spacedir_id
		name = argval
		file_flag = False # true - file;false-not a file
		ref_fodler=None
		return_list=[]
		final_list =[]

		space_object = AntarinSpaces.objects.get(name=spacename)

		all_files = space_object.space_files.all()
		all_folders = space_object.space_folders.all()

		if pk!='':
			folder_object = space_object.space_folders.get(pk=int(pk))
		else:
			folder_object = None


		for file in space_object.space_files.filter(parentfolder=folder_object):
			if os.path.basename(file.file_ref.file.name) == name:
				file_flag = True
				if file.added_by.username == user_object.user.username:
					
					new_spacelog_object = AntarinSpaceLogs(user=user_object.user,space=space_object,action=user_object.user.username + ' deleted file '+ os.path.basename(file.file_ref.file.name))
					new_spacelog_object.save()

					file.delete()
					message = {'message':"File deleted.",'status_code':200}
				else:
					message = api_exceptions.permission_denied()
				return message

		ref_folder = None
		if file_flag == False:
			for folder in space_object.space_folders.filter(parentfolder=folder_object):
				if folder.foldername == name:
					ref_folder = folder
					break
			
			if ref_folder is not None:
				folder_empty_flag = True # True is empty and False is non-empty
				for folder in all_folders:
					if folder.parentfolder == ref_folder:
						folder_empty_flag = False
						break

				if folder_empty_flag:
					for file in all_files:
						if file.parentfolder == ref_folder:
							folder_empty_flag = False
							break

				if folder_empty_flag:
					if ref_folder.added_by.username == user_object.user.username:
						new_spacelog_object = AntarinSpaceLogs(user=user_object.user,space=space_object,action=user_object.user.username + ' deleted folder '+ ref_folder.foldername)
						new_spacelog_object.save()

						ref_folder.delete()
						message = {'message':'Folder deleted.','status_code':200}
					else:
						message = api_exceptions.permission_denied()
					return message

				else:
					#recursive delete
					ref_folder_pk = ref_folder.pk
					ref_folder_name = ref_folder.foldername
					return_list = DeleteView.remove_all_files_dirs_space(user_object,spacename,all_files,all_folders,ref_folder_pk,ref_folder_name)
					if return_list:
						#print(return_list)
						final_list.extend(return_list)
						n = len(return_list)
						i = 0
						while i < n:
						#for i in range(0,len(return_list),2):
							val = DeleteView.remove_all_files_dirs_space(user_object,spacename,all_files,all_folders,return_list[i],return_list[i+1])
							if val:
								return_list.extend(val)
								final_list.extend(val)
								print(return_list,len(return_list))
							i = i + 2
							n = len(return_list)
					print("\n")
					print ("final_list"+str(final_list))
					
					folder_object = space_object.space_folders.get(pk=int(ref_folder_pk))
					print("deleting folder  " + ref_folder_name+ "   "+str(ref_folder_pk))
					new_spacelog_object = AntarinSpaceLogs(user=user_object.user,space=space_object,action=user_object.user.username + ' deleted folder '+ folder_object.foldername)
					new_spacelog_object.save()

					folder_object.delete()
					message = {'message':"Folder deleted.",'status_code':200}
					return message				
						
			else:
				message = api_exceptions.file_DoesNotExist()
				return message

	def remove_all_files_dirs_cloud(user_object,cloud_id,all_files,all_folders,pk,foldername):
	
		cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))

		if pk!='':
			folder_object = cloud_object.cloud_folders.get(pk=int(pk))
		else:
			folder_object = None

		print ("folder object = "+str(folder_object))
		
		for file in all_files:
			if file.parentfolder == folder_object:
				if cloud_object.user.username == user_object.user.username:
					file.delete()
					print("deleted file "+str(file.file_ref.file.name))
				else:
					message = api_exceptions.permission_denied()
					return message
				
		
		return_list=[]
		for item in all_folders:
			if item.parentfolder == folder_object:
				return_list.append(item.pk)
				return_list.append(item.foldername)

		return return_list

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
				output.append(value)
		finally:
			disconnect_all()
		return output

	def get_commands(folders,file_object):
		commands = []
		string_val = ''

		for i in range(len(folders)-1,-1,-1):
			string_val = string_val  + folders[i].foldername + "/"

		commands.append('cd '+string_val+' && rm ' + os.path.basename(file_object.file_ref.file.name))

		return commands

	def delete_cloud_file(user_object,argval,cloud_id,clouddir_id):

		pk = clouddir_id
		name = argval
		file_flag = False # true - file;false-not a file
		ref_fodler=None
		return_list=[]
		final_list =[]

		cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))

		all_files = cloud_object.cloud_files.all()
		all_folders = cloud_object.cloud_folders.all()

		if pk!='':
			folder_object = cloud_object.cloud_folders.get(pk=int(pk))
		else:
			folder_object = None


		for file in cloud_object.cloud_files.filter(parentfolder=folder_object):
			if os.path.basename(file.file_ref.file.name) == name:
				file_flag = True
				if cloud_object.user.username == user_object.user.username:
					

					if cloud_object.package_active != '':
						folders = []
						initialized_cloud_folder_object = AntarinCloudFolders.objects.get(pk=cloud_object.package_active)

						if folder_object:
							while folder_object.parentfolder is not None:
								folders.append(folder_object)
								folder_object = folder_object.parentfolder
						folders.append(folder_object)

						if initialized_cloud_folder_object in folders:
							commands = DeleteView.get_commands(folders,file)
							output = execute(DeleteView.setup_instance,key_path,commands,hosts=cloud_object.dns_name)
							output_text = output[cloud_object.dns_name]

					file.delete()

					message = {'message':"File deleted.",'status_code':200}
				else:
					message = api_exceptions.permission_denied()
				return message

		ref_folder = None
		if file_flag == False:
			for folder in cloud_object.cloud_folders.filter(parentfolder=folder_object):
				if folder.foldername == name:
					ref_folder = folder
					break
			
			if ref_folder is not None:
				folder_empty_flag = True # True is empty and False is non-empty
				for folder in all_folders:
					if folder.parentfolder == ref_folder:
						folder_empty_flag = False
						break

				if folder_empty_flag:
					for file in all_files:
						if file.parentfolder == ref_folder:
							folder_empty_flag = False
							break

				if folder_empty_flag:
					if cloud_object.user.username == user_object.user.username:
						ref_folder.delete()
						message = {'message':'Folder deleted.','status_code':200}
					else:
						message = api_exceptions.permission_denied()
					return message

				else:
					#recursive delete
					ref_folder_pk = ref_folder.pk
					ref_folder_name = ref_folder.foldername
					return_list = DeleteView.remove_all_files_dirs_cloud(user_object,cloud_id,all_files,all_folders,ref_folder_pk,ref_folder_name)
					if return_list:
						#print(return_list)
						final_list.extend(return_list)
						n = len(return_list)
						i = 0
						while i < n:
						#for i in range(0,len(return_list),2):
							val = DeleteView.remove_all_files_dirs_cloud(user_object,cloud_id,all_files,all_folders,return_list[i],return_list[i+1])
							if val:
								return_list.extend(val)
								final_list.extend(val)
								print(return_list,len(return_list))
							i = i + 2
							n = len(return_list)
					print("\n")
					print ("final_list"+str(final_list))

					folder_object = cloud_object.cloud_folders.get(pk=int(ref_folder_pk))


					if cloud_object.package_active != '':
						folders = []
						initialized_cloud_folder_object = AntarinCloudFolders.objects.get(pk=cloud_object.package_active)

						temp_folder_object  = folder_object
						while temp_folder_object.parentfolder is not None and temp_folder_object.parentfolder is not initialized_cloud_folder_object:
							folders.append(temp_folder_object)
							temp_folder_object = temp_folder_object.parentfolder
						folders.append(temp_folder_object)

						if initialized_cloud_folder_object in folders:
							root_path = ''
							commands = []
							for i in range(len(folders)-1,0,-1):
								root_path = root_path  + folders[i].foldername + "/"

							commands.append('cd '+root_path+' && rm -r ' + folder_object.foldername)

							print(commands)
							output = execute(DeleteView.setup_instance,key_path,commands,hosts=cloud_object.dns_name)
							output_text = output[cloud_object.dns_name]

					
					print("deleting folder  " + ref_folder_name+ "   "+str(ref_folder_pk))
					folder_object.delete()

					message = {'message':"Folder deleted.",'status_code':200}
					return message				
						
			else:
				message = api_exceptions.file_DoesNotExist()
				return message

	def delete_space(user_object,argval,pwd):
		
		spaceid = argval
		password = pwd

		username = user_object.user.username
		user_val = User.objects.get(username__exact=username)

		if user_val.check_password(password):
			
			user_space_object = user_object.user.user_spaces.get(access_key=spaceid)
			space_object = user_space_object.space
			space_object.delete()
			
			message = {'message':'Project deleted.','status_code':200}
		
		else:
			print('incorrect password')
			message = api_exceptions.incorrect_password()
		
		return message

	def delete_cloud(user_object,argval,spacename):

		space_object = AntarinSpaces.objects.get(name=spacename)
		
		try:
			user_cloud_object = space_object.space_clouds.get(access_key=int(argval))

			has_permissions = False
			
			if user_cloud_object.user.username == user_object.user.username:
				has_permissions = True

			if not has_permissions:
				message = api_exceptions.permission_denied()
				return message
			
			new_spacelogs_object = AntarinSpaceLogs(user=user_object.user,space=space_object,action=user_object.user.username + ' deleted cloud : '+  user_cloud_object.cloud_name)
			new_spacelogs_object.save()

			user_cloud_object.delete()

			message = {'message':'Cloud deleted.','status_code':200}
		
		except AntarinClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()

		return message

	def get(self,request):
		token = self.request.data['token']
		spaceid = self.request.data['argval'].strip()

		try:
			user_object = Token.objects.get(key=token)
			user_space_object = user_object.user.user_spaces.get(access_key=spaceid)
			if user_space_object.status != 'A':
				message = api_exceptions.permission_denied()
				return Response(message,status=400)
			else:
				message = {'message':'Has permission','status_code':200}
				return Response(message,status=200)
		except UserSpaces.DoesNotExist:
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
					spacedir_id = self.request.data['spacedir_id']
					return_val = DeleteView.delete_project_file(user_object,argval,spacename,spacedir_id)
					
				elif env == 'cloud':
					cloud_id = self.request.data['cloud_id']
					clouddir_id = self.request.data['clouddir_id']
					return_val = DeleteView.delete_cloud_file(user_object,argval,cloud_id,clouddir_id)

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
		space_object = AntarinSpaces.objects.get(name=spacename)
		user_space_object = user_object.user.user_spaces.get(space=space_object)

		if user_space_object.status!='C':
			try:
				contributor_obj = User.objects.get(username=username)
				contributor_space_object = UserSpaces.objects.filter(space=space_object,user=contributor_obj)
				
				if not contributor_space_object:
					all_user_spaces = contributor_obj.user_spaces.all()
					accesskey_list = []
					for item in all_user_spaces:
						accesskey_list.append(item.access_key)

					num = AddView.generate_rand(3)
					while num in accesskey_list:
						num = generate_rand(3)

					access_key = num

					new_userspaces_object = UserSpaces(user=contributor_obj,space=space_object,status='C',access_key=access_key)
					new_userspaces_object.save()
					
					new_spacelogs_object = AntarinSpaceLogs(user=user_object.user,space=space_object,action=user_object.user.username + ' added '+ new_userspaces_object.user.username + ' as contributor.' )
					new_spacelogs_object.save()

					data = {'user':new_userspaces_object.user.username,'acess_key':access_key}
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
		folder_flag = False

		for item in all_folders:
			if item.foldername == foldername and item.parentfolder == parentfolder:
				folder_object = item
				folder_flag = True
				break
		
		if folder_flag == False:
			return -1
		
		return folder_object

	def find_file(filename,parentfolder,all_files):
		file_flag = False
		
		for item in all_files:
			if item.parentfolder == parentfolder and os.path.basename(item.file_ref.file.name) == filename:
				file_object = item
				file_flag = True
				break
		
		if file_flag == False:
			return -1
		
		return file_object

	def add_all(space_object,user_object,folder_object,parentfolder=None):
		all_files = user_object.user.user_files.filter(parentfolder=folder_object)
		all_folders = user_object.user.user_folders.filter(parentfolder=folder_object)

		space_folder_object = AntarinSpaceFolders(space=space_object,foldername=folder_object.foldername,added_by=user_object.user,parentfolder=parentfolder)
		space_folder_object.save()

		for item in all_files:
			space_file_object = AntarinSpaceFiles(space=space_object,file_ref=item.file_ref,parentfolder=space_folder_object,added_by=user_object.user)
			space_file_object.save()

		for item in all_folders:
			AddView.add_all(space_object,user_object,item,space_folder_object)

	def add_to_space(user_object,spacename,item,spacedir_id):

		path = item
		space_object = AntarinSpaces.objects.get(name=spacename)
		folder_flag = False
		file_flag = False
		path_error = False

		if spacedir_id != '':
			root_folder_object = AntarinSpaceFolders.objects.get(pk=int(spacedir_id))
		else:
			root_folder_object = None

		all_folders = user_object.user.user_folders.all()
		all_files = user_object.user.user_files.all()
		error_flag = False

		plist = path
		plist = plist.split('/')
		if path[-1]=='/':
		    plist = plist[:-1]
		print (plist)

		parentfolder = None

		for i in range(1,len(plist)):
			val = AddView.find_folder(plist[i],parentfolder,all_folders)
			if val != -1:
				parentfolder = val
			else:
				path_error = True
		
		if not path_error:
			folder_object = val
			all_spacefolders = AntarinSpaceFolders.objects.filter(space=space_object,parentfolder=root_folder_object)
			
			for item in all_spacefolders:
				if item.foldername == folder_object.foldername:
					error_flag = True
					break

			if error_flag == False:
				AddView.add_all(space_object,user_object,folder_object,root_folder_object)

				new_spacelog_object = AntarinSpaceLogs(user=user_object.user,space=space_object,action=user_object.user.username + ' added directory '+ folder_object.foldername)
				new_spacelog_object.save()
				
				folder_flag = True
				
				message = {'message':'Imported directory.','status_code':200}
				return message
			
			else:
				message = api_exceptions.folder_exists()
				return message

		if not folder_flag:
			
			parentfolder = None
			val = None
			for i in range(1,len(plist)-1):
				print(plist[i],parentfolder)
				val = AddView.find_folder(plist[i],parentfolder,all_folders)
				if val != -1:
					parentfolder = val
				else:
					message = api_exceptions.wrong_path_specified()
					return message
			
			folder_object = val
			file_object = AddView.find_file(plist[-1],folder_object,all_files)
			
			if file_object != -1:
				all_spacefiles = AntarinSpaceFiles.objects.filter(space=space_object,parentfolder=root_folder_object)
				for item in all_spacefiles:
					if os.path.basename(item.file_ref.file.name) == os.path.basename(file_object.file_ref.file.name):
						print("duplicate ref")
						error_flag = True
						break

				if error_flag == False:
					
					new_spacefile_object = AntarinSpaceFiles(space=space_object,file_ref=file_object.file_ref,parentfolder=root_folder_object,added_by=user_object.user)
					new_spacefile_object.save()

					new_spacelogs_object = AntarinSpaceLogs(user=user_object.user,space=space_object,action=user_object.user.username + ' added file '+ os.path.basename(new_spacefile_object.file_ref.file.name))
					new_spacelogs_object.save()

					file_flag = True
					message = {'message':'Imported file.','status_code':200}
					return message
				else:
					message = api_exceptions.file_exists()
					return message
		
		if not folder_flag and not file_flag:
			message = api_exceptions.file_DoesNotExist()
			return message

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
				output.append(value)
		finally:
			print("disconenct worked")
			disconnect_all()
		return output

	def get_commands(folders,new_cloudfile_object):
		commands = []
		string_val = ''

		for i in range(len(folders)-1,-1,-1):
			string_val = string_val  + folders[i].foldername + "/"

		commands.append('cd '+string_val+' && aws s3 cp ' + 's3://antarin-test/media/'+new_cloudfile_object.file_ref.file.name+' '+os.path.basename(new_cloudfile_object.file_ref.file.name))

		return commands

	def add_all_cloud(space_object,cloud_object,folder_object,parentfolder=None,add_to_cloud=None,root_path=None,commands=None,initialized_cloud_folder_object=None):
		all_files = space_object.space_files.filter(parentfolder=folder_object)
		all_folders = space_object.space_folders.filter(parentfolder=folder_object)

		cloud_folder_object = AntarinCloudFolders(cloud=cloud_object,foldername=folder_object.foldername,parentfolder=parentfolder)
		cloud_folder_object.save()

		if root_path:
			print('root_path = '+ root_path)

		if add_to_cloud:
			temp_root_path = root_path
			if parentfolder:
				folders = []
				temp_folder_object = parentfolder
				while temp_folder_object.parentfolder is not None and temp_folder_object.parentfolder is not initialized_cloud_folder_object:
					folders.append(temp_folder_object)
					temp_folder_object = temp_folder_object.parentfolder

				for i in range(len(folders)-1,-1,-1):
					temp_root_path = temp_root_path  + folders[i].foldername + "/"

			commands.append('cd '+temp_root_path + ' && mkdir '+folder_object.foldername)

			temp_root_path = temp_root_path + folder_object.foldername+"/"

		for item in all_files:
			cloud_file_object = AntarinCloudFiles(cloud=cloud_object,file_ref=item.file_ref,parentfolder=cloud_folder_object)
			cloud_file_object.save()

			if add_to_cloud:
				commands.append('cd '+temp_root_path+' && aws s3 cp ' + 's3://antarin-test/media/'+cloud_file_object.file_ref.file.name+' '+os.path.basename(cloud_file_object.file_ref.file.name))

		for item in all_folders:
			if add_to_cloud:
				AddView.add_all_cloud(space_object,cloud_object,item,cloud_folder_object,True,root_path,commands)
			else:				
				AddView.add_all_cloud(space_object,cloud_object,item,cloud_folder_object)

		if add_to_cloud:
			return commands

	def add_to_cloud(user_object,spacename,item,cloud_id,clouddir_id):
		path = item
		space_object = AntarinSpaces.objects.get(name=spacename)
		cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))
		folder_flag = False
		file_flag = False
		path_error = False

		if clouddir_id != '':
			root_folder_object = AntarinCloudFolders.objects.get(pk=int(clouddir_id))
		else:
			root_folder_object = None

		all_folders = space_object.space_folders.all()
		all_files = space_object.space_files.all()
		error_flag = False

		plist = path
		plist = plist.split('/')
		if path[-1]=='/':
		    plist = plist[:-1]
		print (plist)

		parentfolder = None

		for i in range(1,len(plist)):
			val = AddView.find_folder(plist[i],parentfolder,all_folders)
			if val != -1:
				parentfolder = val
			else:
				path_error = True
		
		if not path_error:
			folder_object = val
			all_cloudfolders = AntarinCloudFolders.objects.filter(cloud=cloud_object,parentfolder=root_folder_object)
			
			for item in all_cloudfolders:
				if item.foldername == folder_object.foldername:
					error_flag = True
					break

			if error_flag == False:

				if cloud_object.package_active != '':
					folders = []

					try:
						initialized_cloud_folder_object = AntarinCloudFolders.objects.get(pk=int(cloud_object.package_active))

						temp_folder_object = root_folder_object
						if root_folder_object is not None:
							while temp_folder_object.parentfolder is not None:
								folders.append(temp_folder_object)
								temp_folder_object = temp_folder_object.parentfolder
						folders.append(temp_folder_object)

						if initialized_cloud_folder_object in folders:
							root_path = ''

							for i in range(len(folders)-1,-1,-1):
								root_path = root_path  + folders[i].foldername + "/"

							commands = []
							command_list = AddView.add_all_cloud(space_object,cloud_object,folder_object,root_folder_object,True,root_path,commands,initialized_cloud_folder_object)
							for item in command_list:
								print(item)
							output = execute(AddView.setup_instance,key_path,command_list,hosts=cloud_object.dns_name)
							output_text = output[cloud_object.dns_name]

					except AntarinCloudFolders.DoesNotExist:
						message = api_exceptions.package_deleted()
						return message
				else:
					AddView.add_all_cloud(space_object,cloud_object,folder_object,root_folder_object)
				
				folder_flag = True
				
				message = {'message':'Imported directory.','status_code':200}
				return message
			
			else:
				message = api_exceptions.folder_exists()
				return message

		if not folder_flag:
			
			parentfolder = None
			val = None
			for i in range(1,len(plist)-1):
				print(plist[i],parentfolder)
				val = AddView.find_folder(plist[i],parentfolder,all_folders)
				if val != -1:
					parentfolder = val
				else:
					message = api_exceptions.wrong_path_specified()
					return message
			
			folder_object = val
			file_object = AddView.find_file(plist[-1],folder_object,all_files)
			
			if file_object != -1: 
				all_spacefiles = AntarinCloudFiles.objects.filter(cloud=cloud_object,parentfolder=root_folder_object)
				for item in all_spacefiles:
					if os.path.basename(item.file_ref.file.name) == os.path.basename(file_object.file_ref.file.name):
						print("duplicate ref")
						error_flag = True
						break

				if error_flag == False:
					
					new_cloudfile_object = AntarinCloudFiles(cloud=cloud_object,file_ref=file_object.file_ref,parentfolder=root_folder_object)
					new_cloudfile_object.save()

					if cloud_object.package_active != '':
						folders = []
						initialized_cloud_folder_object = AntarinCloudFolders.objects.get(pk=cloud_object.package_active)

						folder_object = root_folder_object
						if folder_object:
							while folder_object.parentfolder is not None:
								folders.append(folder_object)
								folder_object = folder_object.parentfolder
						folders.append(folder_object)

						if initialized_cloud_folder_object in folders:
							commands = AddView.get_commands(folders,new_cloudfile_object)
							output = execute(AddView.setup_instance,key_path,commands,hosts=cloud_object.dns_name)
							output_text = output[cloud_object.dns_name]

					file_flag = True
					message = {'message':'Imported file.','status_code':200}
					return message
				else:
					message = api_exceptions.file_exists()
					return message
		
		if not folder_flag and not file_flag:
			message = api_exceptions.file_DoesNotExist()
			return message

	def post(self,request):
		token = self.request.data['token']
		argument = self.request.data['argument'].strip()
		env = self.request.data['env'].strip()

		try:
			user_object = Token.objects.get(key = token)
			if argument == 'contributor':
				username = self.request.data['argval']
				spacename = self.request.data['spacename']
				return_val = AddView.add_contributor(user_object,username,spacename)
				
			if argument == '-i':
				item = self.request.data['argval']
				spacename = self.request.data['spacename']
				if env == 'space':
					if item.startswith('~antarin'):
						spacedir_id = self.request.data['spacedir_id']
						return_val = AddView.add_to_space(user_object,spacename,item,spacedir_id)
					else:
						return_val = api_exceptions.wrong_path_specified()

				elif env == 'cloud':
					if item.startswith('~space'):
						cloud_id = self.request.data['cloud_id']
						clouddir_id = self.request.data['clouddir_id']
						return_val = AddView.add_to_cloud(user_object,spacename,item,cloud_id,clouddir_id)
					else:
						return_val = api_exceptions.wrong_path_specified()

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
		client = boto3.resource('ec2', region_name='us-west-2') #added region 
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
		c = boto3.client('ec2', region_name='us-west-2') #added region
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

	def add_files_to_dir(cloud_object,foldername,folderid,commands,parentpath=None):
		if parentpath:
			commands.append('cd '+parentpath+' && mkdir '+foldername)
			print('with cd '+ parentpath)
			print('mkdir ' + foldername)
			parent = parentpath + '/'+foldername
		else:
			commands.append('mkdir '+foldername)
			print('mkdir ' + foldername)
			parent = foldername
		
		folder_object = cloud_object.cloud_folders.get(pk=folderid)
		all_files = cloud_object.cloud_files.filter(parentfolder=folder_object)
		for item in all_files:
			commands.append('cd '+parent+' && aws s3 cp ' + 's3://antarin-test/media/'+item.file_ref.file.name+' '+os.path.basename(item.file_ref.file.name))
			print('with cd '+ parent)
			print('add file '+os.path.basename(item.file_ref.file.name))

			#&& aws s3 cp '+'s3://antarin-test/media/' + item.projectfile.file_ref.file.name + ' ' + os.path.basename(item.projectfile.file_ref.file.name)
		all_folders_list = cloud_object.cloud_folders.filter(parentfolder=folder_object)
		all_folders = []
		for item in all_folders_list:
			all_folders.append(item.foldername)
			all_folders.append(item.pk)
			all_folders.append(parent)
		
		return all_folders,commands

	def post(self,request):
		token = self.request.data['token']
		#print(self.request.data)
		try:
			user_object = Token.objects.get(key = token)
			spacename = self.request.data['spacename']
			
			success = False
			space_object = AntarinSpaces.objects.get(name=spacename)
			accesskey = None
			if 'argval' in self.request.data:
				accesskey = self.request.data['argval'] 
			if accesskey:
				cloud_object = space_object.space_clouds.get(access_key=int(accesskey))
			else:
				cloud_id = self.request.data['cloud_id']
				cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))	

			if cloud_object.user.username != user_object.user.username:
				return_val = api_exceptions.permission_denied()
				message = {'message': return_val,'status_code':400}
				return Response(message,status=400)

			packagename = self.request.data['packagename']
			
			clouddir_id = self.request.data['clouddir_id']
			if clouddir_id != '':
				cloud_root_folder_object = AntarinCloudFolders.objects.get(pk=int(clouddir_id))
			else:
				cloud_root_folder_object = None

			cloud_folder_object = AntarinCloudFolders.objects.get(cloud=cloud_object,parentfolder=cloud_root_folder_object,foldername=packagename)

			if cloud_object.is_active == False:
				sec_group = []
				sec_group.append(cloud_object.security_group)
				key_name = 'ec2test'
				cloud_object.status = 'Initializing'
				cloud_object.save()
				res = execute(InitializeView.launch_instance,cloud_object.ami_id,key_name,cloud_object.instance_type,sec_group)

				if res['localhost'][0]:
					dns_name = res['localhost'][0][0]
					instance_id_val = res['localhost'][1][0]
					cloud_object.dns_name = res['localhost'][0][0]
					cloud_object.instance_id = instance_id_val
					cloud_object.is_active = True
					print("er")
					cloud_object.save()
					print("her")				
					folder_object = cloud_folder_object
					folder_name = folder_object.foldername
					folder_id = folder_object.pk
					commands = []
					value = InitializeView.add_files_to_dir(cloud_object,folder_name,folder_id,commands)
					all_folders = value[0]
					final_list = []
					commands = value[1]
					if all_folders:
						n = len(all_folders)
						i = 0
						final_list.extend(all_folders)
						while i<n:
							val = InitializeView.add_files_to_dir(cloud_object,all_folders[i],all_folders[i+1],commands,all_folders[i+2])
							if val:
								all_folders.extend(val[0])
								final_list.extend(val[0])
								commands = val[1]
								#print(all_folders,final_list)
							i += 3
							n = len(all_folders)
					
					for command in commands:
						print(command)
					
					all_files = cloud_object.cloud_files.filter(parentfolder=folder_object)
					for item in all_files:
						if os.path.basename(item.file_ref.file.name) == 'requirements.txt':
							commands.append('cd ' + packagename +' && sudo pip install -r requirements.txt')
							break

					output = execute(InitializeView.setup_instance,key_path,commands,hosts = cloud_object.dns_name)
					print(output)
					
					cloud_object.status = 'Initialized with package: ' + packagename
					cloud_object.package_active = str(folder_id)
					cloud_object.save()

					message = {'message': 'Session initilization successful.','status_code':200}
					return Response(message,status=200)
				
				else:
					message = api_exceptions.intance_launch_error()
					return Response(message,status=400)
			else:
				folder = AntarinCloudFolders.objects.get(pk=int(cloud_object.package_active))
				message = {'message': 'Session has been already initialized with package : ' + folder.foldername,'status_code':200}
				return Response(message,status=200)

		except AntarinCloudFolders.DoesNotExist:
			message = api_exceptions.package_DoesNotExist()
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
				output.append(value)
		finally:
			print("disconenct worked")
			disconnect_all()
		return output

	def post(self,request):
		token = self.request.data['token']
		#print(self.request.data)
		try:
			user_object = Token.objects.get(key = token)
			spacename = self.request.data['spacename']
			packagename = self.request.data['packagename']
			shell_command = self.request.data['shell_command']
			commands = []
			
			space_object = AntarinSpaces.objects.get(name=spacename)
			accesskey = None
			if 'argval' in self.request.data:
				accesskey = self.request.data['argval'] 
			if accesskey:
				cloud_object = space_object.space_clouds.get(access_key=int(accesskey))
			else:
				cloud_id = self.request.data['cloud_id']
				cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))	

			clouddir_id = self.request.data['clouddir_id']
			if clouddir_id != '':
				cloud_root_folder_object = AntarinCloudFolders.objects.get(pk=int(clouddir_id))
			else:
				cloud_root_folder_object = None

			folder_object = AntarinCloudFolders.objects.get(cloud=cloud_object,parentfolder=cloud_root_folder_object,foldername=packagename)

			if cloud_object.is_active == True:
				cloud_object.process_running = shell_command
				cloud_object.status = 'Exceuting process : ' + shell_command
				cloud_object.save()
				commands.append(shell_command)
				output = execute(RunView.setup_instance,key_path,commands,hosts = cloud_object.dns_name)
				output_text = output[cloud_object.dns_name]
				for item in output_text:
					print(item)

				cloud_object.status = 'Task Complete : ' + shell_command
				cloud_object.save()

				message = {'message': output_text,'status_code':200}
				return Response(message,status=200)
			
			else:
				message = api_exceptions.cloud_notRunning()
				return Response(message,status=400)

		except AntarinCloudFolders.DoesNotExist:
			message = api_exceptions.package_DoesNotExist()
			return Response(message,status=400)
		except SystemExit:
			message = "error"
			return Response(message,status=400)
		except AntarinClouds.DoesNotExist:
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
			spacename = self.request.data['spacename']
			space_object = AntarinSpaces.objects.get(name=spacename)
			accesskey = None
			if 'argval' in self.request.data:
				accesskey = self.request.data['argval'] 
			if accesskey:
				cloud_object = space_object.space_clouds.get(access_key=int(accesskey))
			else:
				cloud_id = self.request.data['cloud_id']
				cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))

			if cloud_object.is_active == True:
				cloud_id = []
				cloud_id.append(cloud_object.instance_id)
				client = boto3.client('ec2')
				response = client.stop_instances(InstanceIds=cloud_id)
				cloud_object.is_active = False
				cloud_object.dns_name = ''
				cloud_object.instance_id = ''
				cloud_object.package_active = ''
				cloud_object.process_running = ''
				cloud_object.status = 'Standby'
				cloud_object.save()
				print (response)
				message = {'message':'Session ended.','status_code':200}
				return Response(message,status=200)
			else:
				message = api_exceptions.instance_not_running()
				return Response(message,status=400)
		except AntarinClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)


class CloneView(APIView):

	def clone_all(new_cloud_folder_object,cloud_object,item,cloned_object):
		print(cloud_object.cloud_name)
		all_files = AntarinCloudFiles.objects.filter(cloud=cloud_object,parentfolder=item)
		all_folders = AntarinCloudFolders.objects.filter(cloud=cloud_object,parentfolder=item)
		print(all_files,all_folders)
		for item in all_files:
			new_cloudfile_object = AntarinCloudFiles(cloud=cloned_object,file_ref=item.file_ref,parentfolder=new_cloud_folder_object)
			new_cloudfile_object.save()

		for item in all_folders:
			new_cloud_folder_object = AntarinCloudFolders(cloud=cloned_object,foldername=item.foldername,parentfolder=new_cloud_folder_object)
			new_cloud_folder_object.save()
			CloneView.clone_all(new_cloud_folder_object,cloud_object,item,cloned_object)

	def generate_rand(n):
		llimit = 10**(n-1)
		ulimit = (10**n)-1
		return random.randint(llimit,ulimit)

	def post(self,request):
		token = self.request.data['token']
		try:
			user_object = Token.objects.get(key = token)
			accesskey = self.request.data['argval']
			spacename = self.request.data['spacename']
			space_object = AntarinSpaces.objects.get(name=spacename)
			
			cloud_object = space_object.space_clouds.get(access_key=int(accesskey))
			all_space_clouds = space_object.space_clouds.all()

			accesskey_list = []
			for item in all_space_clouds:
				accesskey_list.append(item.access_key)

			access_key_length = 3
			num = CloneView.generate_rand(access_key_length)
			while num in accesskey_list:
				num = CloneView.generate_rand(access_key_length)

			access_key = num

			cloud_object_copy = copy.deepcopy(cloud_object)
			all_cloud_folders = cloud_object.cloud_folders.all()
			all_cloud_files = cloud_object.cloud_files.all()
			all_home_files = cloud_object.cloud_files.filter(parentfolder=None)
			all_home_folders = cloud_object.cloud_folders.filter(parentfolder=None)

			cloned_object = cloud_object
			cloned_object.access_key = num
			cloned_object.cloud_name = cloud_object.cloud_name + '(cloned)'
			cloned_object.pk = None
			cloned_object.instance_id = ''
			cloned_object.dns_name = ''
			cloned_object.is_active = False
			cloned_object.space = cloud_object.space
			cloned_object.user = user_object.user
			cloned_object.package_active = ''
			cloned_object.save()

			for item in all_home_files:
				new_cloudfile_object = AntarinCloudFiles(cloud=cloned_object,file_ref=item.file_ref,parentfolder=None)
				new_cloudfile_object.save()

			for item in all_home_folders:
				new_cloud_folder_object = AntarinCloudFolders(cloud=cloned_object,foldername=item.foldername,parentfolder=None)
				new_cloud_folder_object.save()

				CloneView.clone_all(new_cloud_folder_object,cloud_object_copy,item,cloned_object)
			
			message = {'message': cloned_object.access_key,'status_code':200}
			return Response(message,status=200)

		except AntarinClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class MergeView(APIView):

	def clone_all(new_cloud_folder_object,source_cloud_object,item,destination_cloud_object):
		all_files = AntarinCloudFiles.objects.filter(cloud=source_cloud_object,parentfolder=item)
		all_folders = AntarinCloudFolders.objects.filter(cloud=source_cloud_object,parentfolder=item)
		
		for item in all_files:
			new_cloudfile_object = AntarinCloudFiles(cloud=destination_cloud_object,file_ref=item.file_ref,parentfolder=new_cloud_folder_object)
			new_cloudfile_object.save()

		for item in all_folders:
			new_cloud_folder_object = AntarinCloudFolders(cloud=destination_cloud_object,foldername=item.foldername,parentfolder=new_cloud_folder_object)
			new_cloud_folder_object.save()
			CloneView.clone_all(new_cloud_folder_object,source_cloud_object,item,destination_cloud_object)

	def post(self,request):
		token = self.request.data['token']
		try:
			user_object = Token.objects.get(key = token)
			spacename = self.request.data['spacename']
			
			space_object = AntarinSpaces.objects.get(name=spacename)
			
			source_access_key = self.request.data['source_id']
			destination_access_key = self.request.data['destination_id']
			
			source_cloud_object = space_object.space_clouds.get(access_key=int(source_access_key))
			destination_cloud_object = space_object.space_clouds.get(access_key=int(destination_access_key))

			all_source_cloud_folders = source_cloud_object.cloud_folders.all()
			all_source_cloud_files = source_cloud_object.cloud_files.all()
			all_home_files = source_cloud_object.cloud_files.filter(parentfolder=None)
			all_home_folders = source_cloud_object.cloud_folders.filter(parentfolder=None)

			for item in all_home_files:
				new_cloudfile_object = AntarinCloudFiles(cloud=destination_cloud_object,file_ref=item.file_ref,parentfolder=None)
				new_cloudfile_object.save()

			for item in all_home_folders:
				new_cloud_folder_object = AntarinCloudFolders(cloud=destination_cloud_object,foldername=item.foldername,parentfolder=None)
				new_cloud_folder_object.save()

				MergeView.clone_all(new_cloud_folder_object,source_cloud_object,item,destination_cloud_object)

			message = {'message': 'Merge successful!','status_code':200}
			return Response(message,status=200)

		except AntarinClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)


class DownloadView(APIView):
	def post(self,request):
		token = self.request.data['token']
		argval = self.request.data['argval'].strip()
		env = self.request.data['env'].strip()
		file_object = None
		found = False
		try:
			user_object = Token.objects.get(key=token)
			
			if env == 'filesystem':
				#look for filename in userfiles
				dir_id = self.request.data['id']
				if dir_id:
					user_folder_object = UserFolders.objects.get(pk=int(dir_id))
				else:
					user_folder_object = None
				
				all_files = user_object.user.user_files.filter(parentfolder=user_folder_object)
				for item in all_files:
					if os.path.basename(item.file_ref.file.name) == argval:
						file_object = item
						found = True
						break
			
			elif env == 'space':
				#look for filename in projectfiles
				spacename = self.request.data['spacename'].strip()
				space_object = AntarinSpaces.objects.get(name=spacename)
				spacedir_id = self.request.data['spacedir_id']

				if spacedir_id:
					space_folder_object = AntarinSpaceFolders.objects.get(pk=int(spacedir_id))
				else:
					space_folder_object = None
				
				all_files = space_object.space_files.filter(parentfolder=space_folder_object)
				for item in all_files:
					if os.path.basename(item.file_ref.file.name) == argval:
						file_object = item
						found = True
						break

			elif env == 'cloud':
				#look for filename in cloudfiles
				cloud_id = self.request.data['cloud_id']
				cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))
				clouddir_id = self.request.data['clouddir_id']
				
				if clouddir_id:
					cloud_folder_object = AntarinCloudFolders.objects.get(pk=int(clouddir_id))
				else:
					cloud_folder_object = None
				
				all_files = cloud_object.cloud_files.filter(parentfolder=cloud_folder_object)
				for item in all_files:
					if os.path.basename(item.file_ref.file.name) == argval:
						file_object = item
						found = True
						break
			
			if not found:
				message = api_exceptions.file_DoesNotExist()
				return Response(message,status=400)

			url = file_object.file_ref.file.url
			message = {'message':url,'status_code':200}
			return Response(message,status=200)
		except AntarinSpaces.DoesNotExist:
			message = api_exceptions.project_DoesNotExist()
			return Response(message,status=400)
		except AntarinClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

class MonitorView(APIView):

	def post(self,request):
		token = self.request.data['token']
		env = self.request.data['env'].strip()
		try:
			user_object = Token.objects.get(key=token)
			return_val = []
			all_clouds=[]
			if env == 'filesystem':
				all_clouds = user_object.user.user_clouds.all()
			if env == 'space':
				spacename = self.request.data['spacename']
				space_object = AntarinSpaces.objects.get(name=spacename)
				all_clouds = space_object.space_clouds.all()
			if env =='cloud':
				cloud_id = self.request.data['cloud_id']
				cloud_object = AntarinClouds.objects.get(pk=int(cloud_id))
				all_clouds .append(cloud_object)
			
			for item in all_clouds:
				return_val.append((item.cloud_name,item.space.name,item.status))

			message = {'message':return_val,'status_code':200}
			return Response(message,status=200)

		except AntarinSpaces.DoesNotExist:
			message = api_exceptions.project_DoesNotExist()
			return Response(message,status=400)
		except AntarinClouds.DoesNotExist:
			message = api_exceptions.instance_DoesNotExist()
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = api_exceptions.invalid_session_token()
			return Response(message,status=404)

