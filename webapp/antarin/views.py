#AUTHOR : RUCHIKA SHIVASWAMY

'''
This file contains all views defined for 'antarin' application
'''
from django.shortcuts import render_to_response, get_object_or_404,render
from antarin.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from datetime import datetime
import hashlib,random,json,boto,os
from antarin.models import *
from django.utils import timezone
from django.conf import settings
from antarin.serializers import FetchFilesSerializer
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser
from hurry.filesize import size
from boto.s3.connection import S3Connection, Bucket, Key
from wsgiref.util import FileWrapper


#S3 Bucket details
conn = S3Connection(settings.AWS_ACCESS_KEY_ID , settings.AWS_SECRET_ACCESS_KEY)
b = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
k = Key(b)


'''
To manage the data entered in AuthenticationForm. If the form was submitted(http POST) and returned without validation errors, then the user is authenticated and redirected to his homepage.
'''
@csrf_protect
def login_view(request):
	form = AuthenticationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = form.login(request)
		if user:
			login(request,user)
			return HttpResponseRedirect("/home")		

	variables = RequestContext(request,{'form':form})
	return render_to_response('registration/login.html',variables,)

'''
To manage user registration. All data submitted to the form is entered into a dictionary. In addition to these, the dictionary is also updated with 
activation_key and email_subject values. This method then calls the methods sendEmail() and save() defined in Registration Form class by which an email
is sent to the user and all his data is saved to the User database.
'''
@csrf_protect
def signup(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			userdata = {}
			userdata['username'] = form.cleaned_data['username']
			userdata['password'] = form.cleaned_data['password']
			userdata['firstname'] = form.cleaned_data['firstname']
			userdata['lastname'] = form.cleaned_data['lastname']
			keyval = (hashlib.sha1((str(random.random())).encode('utf8')).hexdigest()[:5]).encode('utf8')
			usernamekey = userdata['username']
			if isinstance(usernamekey,str):
				usernamekey = usernamekey.encode('utf8')
			userdata['activation_key'] = hashlib.sha1(keyval+usernamekey).hexdigest()
			userdata['email_subject'] = "Welcome to antarinX!"
			form.sendEmail(userdata)
			form.save(userdata)
			return HttpResponseRedirect('./success')
	else:
		form = RegistrationForm()
	variables = RequestContext(request,{'form':form})
	return render_to_response('registration/signup.html',variables,)

'''
This view defines logic for the page that is rendered when a user clicks on the activation link that was emailed to him when creating his antarin profile.
The parameter that was passed in the url (activation key) is used to fetch the corresponding userprofile and set his status to active if the link was clicked within 48 hours.
'''
def activation(request,key):
	#print(key)
	activation_expired=False
	active = False
	userprofile = get_object_or_404(UserProfile, activation_key=key)
	if userprofile.user.is_active == False:
		if timezone.now() > userprofile.key_expires:
			activation_expired = True
			id_user = userprofile.user.id
		else:
			userprofile.user.is_active = True
			userprofile.user.save()
	else:
		active = True
	return render(request, 'activation.html', locals())

'''View rendered for the page after successful registration i.e after the user submitted his form and an email contaning an activation key was sent to him '''
def signup_success(request):
	return render_to_response('registration/success.html',)

'''
To manage the data submitted through the password reset form. In addition to the value entered by th user in the form, his username, a password reset key
is generated and stored in a dictionary. This method then calls the sendEmail() and save() methods defined in PasswordResetForm class. An email is sent to the user and his profile is updated with the passsword reset key that was generated.
'''
@csrf_protect
def password_reset(request):
	if request.method == 'POST':
		form = PasswordResetForm(request.POST)
		if form.is_valid():
			userdata = {}
			userdata['username'] = form.cleaned_data['username'].lower()
			userdata['firstname'] = form.getFirstname(userdata['username'])
			keyval = (hashlib.sha1((str(random.random())).encode('utf8')).hexdigest()[:9]).encode('utf8')
			usernamekey = userdata['username']
			if isinstance(usernamekey,str):
				usernamekey = usernamekey.encode('utf8')
			userdata['password_reset_key'] = hashlib.sha1(keyval+usernamekey).hexdigest()
			userdata['email_subject'] = "antarinX reset your Password "
			form.sendEmail(userdata)
			form.save(userdata)
			return HttpResponseRedirect('./redirect/')
	else:
		form = PasswordResetForm()
	variables = RequestContext(request,{'form':form})
	return render_to_response('registration/password_reset.html', variables,)

'''
The page that is rendered after a user submits his email address requesting for a password reset.
'''
def password_reset_redirect(request):
	return render_to_response('password_reset_redirect.html',)

'''
This view defines logic for the page that is rendered when a clicks on the link that was emailed to him to perform a password reset operation.
It uses th parameter that was passed through the URL(password_reset_key) and fetches the corresponding userprofile object from User database. A set_password()
method is called on the object that was returned and the new password is saved to the user database.
'''
@csrf_protect
def password_key_activation(request,key):
	if request.method == 'POST':
		form = PasswordEntryForm(request.POST)
		if form.is_valid():
			userprofile = get_object_or_404(UserProfile,password_reset_key = key)
			userprofile.user.set_password(form.cleaned_data['password1'])
			userprofile.user.save()
			return render_to_response('password_reset_success.html',)
	else:
		form = PasswordEntryForm()
	variables = RequestContext(request,{'form':form})
	return render_to_response('passwordEntry.html',variables,)

def password_reset_success(request):
	return render_to_response('password_reset_success.html')


def calculate_used_data_storage(all_files):
	total_val = 0
	for file in all_files:
		total_val = total_val + file.file.size
	return size(total_val)
'''
This view defines the customised user homepage that is rendered on a successful user login. The @login_required decorator ensurest that this view is
only excuted when a user is logged in.
'''
# @login_required
# def userHomepage(request):
# 	user = User.objects.get(username = request.user.username)
# 	all_files = user.useruploadedfiles.all()
# 	used_data_storage = calculate_used_data_storage(all_files)
# 	user.data_storage_used = used_data_storage
# 	user.save()
# 	if request.method == 'POST':
# 		form = FileUploadForm(request.POST,request.FILES)
# 		if form.is_valid():
# 			user_files = UserUploadedFiles()
# 			user_files.user = user
# 			user_files.file = request.FILES.get('file')
# 			user_files.save()
# 			all_files = user.useruploadedfiles.all()
# 			used_data_storage = calculate_used_data_storage(all_files)
# 			user.data_storage_used = used_data_storage
# 			user.save()
# 			message = "Files were uploaded successfully!"
# 			variables = RequestContext(request,{'form':form,'message':message,'media_url':settings.MEDIA_URL,"allfiles":all_files,"used_data_storage":used_data_storage,"total_data_storage":user.userprofile.total_data_storage})
# 			return render_to_response('home.html',variables)
# 	else:
# 		form = FileUploadForm()
# 	variables = RequestContext(request,{'form':form,'media_url':settings.MEDIA_URL,"allfiles":all_files,"used_data_storage":used_data_storage,"total_data_storage":user.userprofile.total_data_storage})
# 	return render_to_response('home.html',variables)

@login_required
def userHomepage(request):
	user = User.objects.get(username = request.user.username)
	all_files = user.useruploadedfiles.all()
	used_data_storage = calculate_used_data_storage(all_files)
	user.data_storage_used = used_data_storage
	user.save()
	if request.method == 'POST':
		form = FileUploadForm(request.POST,request.FILES)
		if form.is_valid():
			user_files = UserUploadedFiles()
			user_files.user = user
			user_files.file = request.FILES.get('file')
			user_files.folder = None
			user_files.save()
			all_files = user.useruploadedfiles.all()
			used_data_storage = calculate_used_data_storage(all_files)
			user.data_storage_used = used_data_storage
			user.save()
			message = "Files were uploaded successfully!"
			variables = RequestContext(request,{'form':form,'message':message,'media_url':settings.MEDIA_URL,"allfiles":all_files,"used_data_storage":used_data_storage,"total_data_storage":user.userprofile.total_data_storage})
			return render_to_response('home.html',variables)
	else:
		form = FileUploadForm()
	variables = RequestContext(request,{'form':form,'media_url':settings.MEDIA_URL,"allfiles":all_files,"used_data_storage":used_data_storage,"total_data_storage":user.userprofile.total_data_storage})
	return render_to_response('home.html',variables)

# class ListFilesView(APIView):
# 	def get(self,request):
# 		try:
# 			user_val = Token.objects.get(key = self.request.data)
# 			all_files = user_val.user.useruploadedfiles.all()
# 			return_val = [file.file.name for file in all_files]
# 			print(return_val)
# 			return Response(return_val)
# 		except Token.DoesNotExist:
# 			return None

class ListFilesView(APIView):
	def post(self,request):
		token = self.request.data['token']
		pk = self.request.data['id']
		env_flag = int(self.request.data['env_flag'])
		projectname = self.request.data['env_name']
		pid = self.request.data['pid']
		try:
			user_object = Token.objects.get(key = token)
			if env_flag: #inside project environment
				list_val=[]
				print (projectname)
				project_object = Projects.objects.get(name=projectname)
				if pid != "":
					project_folder_object = project_object.projectfolders.get(pk=int(pid))
				else:
					project_folder_object = None

				if project_folder_object is None:
					all_projectfiles = project_object.projectfiles.all()
					all_projectfolders = project_object.projectfolders.all()

					for file in all_projectfiles:
						list_val.append(os.path.basename(file.file_ref.file.name))

					for folder in all_projectfolders:
						list_val.append("/"+folder.folder_ref.name)
					
					message = {'message':list_val,'status_code':200}
					return Response(message,status=200)
				else:
					folder_object = project_folder_object.folder_ref
					usr_obj = folder_object.user
					for file in usr_obj.useruploadedfiles.all():
						if file.folder == folder_object:
							list_val.append(os.path.basename(file.file.name))
				
					for folder in usr_obj.userfolders.all():
						if folder.parentfolder == folder_object:
							list_val.append("/"+folder.name)
					
					message = {'message':list_val,'status_code':200}
					return Response(message,status=200)
			else:#inside file system environment
				list_val = []
				if pk != "":
					folder_object = user_object.user.userfolders.get(pk=int(pk))
				else:
					folder_object = None
				
				for file in user_object.user.useruploadedfiles.all():
					if file.folder == folder_object:
						list_val.append(os.path.basename(file.file.name))
				
				for folder in user_object.user.userfolders.all():
					if folder.parentfolder == folder_object:
						list_val.append("/"+folder.name)
				
				message = {'message':list_val,'status_code':200}
				return Response(message,status=200)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)
		
class UploadFileView(APIView):
	def post(self,request):
		token = request.data['token']
		foldername = self.request.data['foldername']
		pk = self.request.data['id']
		try:
			user_object = Token.objects.get(key = token)
			if pk != "":
				folder_object = user_object.user.userfolders.get(pk=int(pk))
			else:
				folder_object = None

			dup_name_flag = 0
			all_folders_inside_currdir = user_object.user.userfolders.filter(parentfolder=folder_object)
			for  item in all_folders_inside_currdir:
				if item.name == foldername:
					dup_name_flag = 1
					break
					print("duplicate names")
			if dup_name_flag:
				message = {'message':"ERROR: Folder exists.",'status_code':400}
				return Response(message,status=400)
			message = {'message':"File upload successful.",'status_code':200}
			return Response(message,status=200)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)

	def put(self, request,format=None):
		file_object = request.data['file']
		token = request.data['token'].strip('"')
		pk = request.data['id_val'].strip('"')
		env_flag = int(request.data['env_flag'].strip('"'))
		filename = request.data['filename'].strip('"')
		print(filename)
		if ' ' in filename:
			filename = filename.replace(' ','_')
		file_flag = request.data['file_flag'].strip('"')
		try:
			user_val = Token.objects.get(key = token)
			if env_flag:
				pass
			else:
				if pk!="":
					folder_object = user_val.user.userfolders.get(pk=int(pk))
					#print(str(folder_object.pk),str(folder_object.name))
				else:
					folder_object = None

				if file_flag:
					all_files_in_currdir = user_val.user.useruploadedfiles.filter(folder=folder_object)
					dup_name_flag = 0
					for item in all_files_in_currdir:
						if os.path.basename(item.file.file.name) == filename:
							dup_name_flag = 1
							break
					if dup_name_flag:
						message = {'message':"ERROR: File exists.",'status_code':400}
						return Response(message,status=400)

				user_files = UserUploadedFiles()
				user_files.user = user_val.user
				user_files.file = file_object
				user_files.file.name = filename
				user_files.folder = folder_object
				#print(user_val.user.userprofile.data_storage_used)

				all_files = user_val.user.useruploadedfiles.all()
				used_data_storage = calculate_used_data_storage(all_files)
				user_val.user.userprofile.data_storage_used = str(used_data_storage)
				user_val.user.save()
				user_val.user.userprofile.save()
				user_files.save()
				#print("Uploaded file " + str(file_object) + "inside folder with pk = "+ str(folder_object.pk) + " name = " +str(folder_object.name))
				#print("Success!")
				#print(user_val.user.userprofile.data_storage_used)
				#catch error when save didn't work fine and return status 400
				print("\n")
				message = {'message':"File upload successful.",'status_code':204}
				return Response(message,status=204)
		except Token.DoesNotExist:
			message = {'message':'ERROR: Session token is not valid.','status_code':404}
			return Response(message,status=404)


class UserSummaryView(APIView):
	def post(self,request):
		token = self.request.data['token']
		env_flag = int(self.request.data['env_flag'])
		projectname = self.request.data['env_name']
		try:
			user_object = Token.objects.get(key=token)
			if env_flag:#project env
				try:
					project_object = Projects.objects.get(name=projectname)
					all_userproject_objects = project_object.projectdetails.all()
					all_projectfiles = project_object.projectfiles.all()
					all_projectfolders = project_object.projectfolders.all()
					
					contributor_list=[]
					file_list=[]
					folder_list=[]
					admin = ''

					for item in all_userproject_objects:
						contributor_list.append((item.user.username,item.status))
						if item.status == 'A':
							admin = item.user.first_name + ' '+ item.user.last_name +'('+item.user.username+')'

					for item in all_projectfiles:
						file_list.append((os.path.basename(item.file_ref.file.name),item.file_ref.user.first_name+' '+item.file_ref.user.last_name+'('+item.file_ref.user.username+')'))

					for item in all_projectfolders:
						folder_list.append(('/'+item.folder_ref.name,item.folder_ref.user.first_name+ ' '+item.folder_ref.user.last_name+'('+item.folder_ref.user.username+')'))

					data = {'projectname':projectname,'contributors':contributor_list,'admin':admin,'file_list':file_list,'folder_list':folder_list}
					print (file_list)
					print(folder_list)
					message = {'message':data,'status_code':200}
					return Response(message,status=200)
				except Projects.DoesNotExist:
					message = {'message':"ERROR: Project does not exist",'status_code':404}
					return Response(message,status=404)
			else:
				user_data = {'firstname':user_object.user.first_name,
							 'lastname':user_object.user.last_name,
							 'username':user_object.user.username,
							 'data_storage_available':user_object.user.userprofile.total_data_storage,
							 'data_storage_used':user_object.user.userprofile.data_storage_used
							}
				#user_data = (user_object.user.first_name,user_object.user.last_name,user_object.user.username,user_object.user.userprofile.total_data_storage,user_object.user.userprofile.data_storage_used)
				#print(user_data)
				message = {'message':user_data,'status_code':200}
				return Response(message,status=200)
		except Token.DoesNotExist:
			message = {'message':'ERROR:Session token is not valid.','status_code':404}
			return Response(message,status=404)


class LogoutView(APIView):
	def post(self,request):
		try:
			instance = Token.objects.get(key=self.request.data['token'])
			instance.delete()
			message = {'message':'Token deleted. Logout Successful.','status_code':204}
			return Response(message,status=204)
		except Token.DoesNotExist:
			message = {'message':'ERROR:Session token is not valid.','status_code':404}
			return Response(message,status=404)

class CreateDirectoryView(APIView):
	def post(self,request):
		token = self.request.data['token']
		foldername = self.request.data['foldername']
		pk = self.request.data['id']
		env_flag = int(self.request.data['env_flag'])
		count = None
		alt_foldername = None
		if 'count' in self.request.data:
			count = int(self.request.data['count'])
		if 'alt_foldername' in self.request.data:
			alt_foldername = self.request.data['alt_foldername']
			foldername = alt_foldername
		print(count,alt_foldername)
		try:
			user_object = Token.objects.get(key = token)
			if env_flag:
				pass
			else:
				if pk != "":
					folder_object = user_object.user.userfolders.get(pk=int(pk))
				else:
					folder_object = None

				dup_name_flag = 0
				all_folders_inside_currdir = user_object.user.userfolders.filter(parentfolder=folder_object)
				for  item in all_folders_inside_currdir:
					if item.name == foldername:
						dup_name_flag = 1
						break
						print("duplicate names")
				if dup_name_flag:
					message = {'message':"ERROR: Folder exists.",'status_code':400}
					return Response(message,status=400)
				if count==0:
					#print("here -- count=0")
					new_folder_object = UserFolder(user=user_object.user,name=alt_foldername,parentfolder=folder_object)
				else:
					new_folder_object = UserFolder(user=user_object.user,name=foldername,parentfolder=folder_object)
				new_folder_object.save()
				data = {'id':new_folder_object.pk}
				message = {'message':json.dumps(data),'status_code':200}
				#print ("created directory {0} with pk {1} and parentfodler {2}" .format(new_folder_object.name,new_folder_object.pk,new_folder_object.parentfolder.name))
				return Response(message,status=200)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)

class ChangeDirectoryView(APIView):
	def post(self,request):
		flag = 0
		token = self.request.data['token']
		foldername = self.request.data['foldername']
		pk = self.request.data['id']
		env_flag =int(self.request.data['env_flag'])
		projectname = self.request.data['env_name']
		pid = self.request.data['pid']
		#print(foldername,pk)
		try:
			user_object = Token.objects.get(key=token)
			if env_flag:
				try:
					project_object = Projects.objects.get(name=projectname)
					all_projectfolders = project_object.projectfolders.all()
					folder_flag=0
					for item in all_projectfolders:
						if item.folder_ref.name == foldername:
							folder_object = item
							folder_flag=1
							break
					if folder_flag:
						data = {'pid':folder_object.pk}
						message = {'message':json.dumps(data),'status_code':200}
						return Response(message,status=200)
					else:
						message = {'message':"ERROR: Folder does not exist in this project",'status_code':404}
						return Response(message,status=404)
				except Projects.DoesNotExist:
					message = {'message':"ERROR: Project does not exist",'status_code':404}
					return Response(message,status=404)

			else: #inside filesystem env
				if pk != "":
					folder_object = user_object.user.userfolders.get(pk=int(pk))
				else:
					folder_object = None
				if foldername == '..':
					if folder_object.parentfolder is not None:
						current_directory = folder_object.parentfolder.name
						id_val = folder_object.parentfolder.pk
					else:
						current_directory = "/antarin"
						id_val = ""
					data = {'current_directory':current_directory,'id':id_val}
					message = {'message':json.dumps(data),'status_code':200}
					return Response(message,status=200)
				else:
					all_folders = user_object.user.userfolders.all()
					for folder in all_folders:
						if folder.parentfolder == folder_object and folder.name == foldername:
							current_directory = folder.name
							id_val = folder.pk
							data = {'current_directory':current_directory,'id':id_val}
							flag = 1
							break
					if flag==1:
						message = {'message':json.dumps(data),'status_code':200}
						return Response(message,status=200)
					else:
						return Response("ERROR: Folder does not exist.",status=404)
		except Token.DoesNotExist:			
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)


class CurrentWorkingDirectoryView(APIView):
	def post(self,request):
		token = self.request.data['token']
		pk = self.request.data['id']
		env_flag = int(self.request.data['env_flag'])
		projectname = self.request.data['env_name']
		pid = self.request.data['pid']
		if projectname:
			nameval = projectname.split(':')[1]
		try:
			user_object = Token.objects.get(key=token)
			if env_flag:
				project_object = Projects.objects.get(name=projectname)
				if pid != "":
					path_val = []
					string_val = ""
					folder_object = user_object.user.userfolders.get(pk=int(pid))
					while folder_object.parentfolder is not None:
						path_val.append(folder_object.name)
						folder_object = folder_object.parentfolder
					path_val.append(folder_object.name)
					for i in range(len(path_val)-1,-1,-1):
						string_val = string_val + "/" + path_val[i]
					#print(string_val)
					message = {'message':json.dumps(nameval + ' : /'+string_val),'status_code':200}
					return Response(message,status=200)
					
				else:
					message = {'message':json.dumps(nameval + ' : /'),'status_code':200}
					return Response(message,status=200)
			else:
				if pk != "":
					path_val = []
					string_val = ""
					folder_object = user_object.user.userfolders.get(pk=int(pk))
					while folder_object.parentfolder is not None:
						path_val.append(folder_object.name)
						folder_object = folder_object.parentfolder
					path_val.append(folder_object.name)
					for i in range(len(path_val)-1,-1,-1):
						string_val = string_val + "/" + path_val[i]
					#print(string_val)
					message = {'message':json.dumps('~antarin'+string_val),'status_code':200}
					return Response(message,status=200)
				else:
					folder_object = None
					message = {'message':json.dumps('~antarin'),'status_code':200}
					return Response(message,status=200)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)

class RemoveObjectView(APIView):

	def remove_all_files_dirs(token,all_files,all_folders,pk,foldername):
		print("Inside remove all function" + "\t" + foldername)
		user_object = Token.objects.get(key=token)
		if pk!='':
			folder_object = user_object.user.userfolders.get(pk=int(pk))
		else:
			folder_object = None
		#folder_object = user_object.user.userfolders.get(pk=int(pk))
		print ("folder object = "+str(folder_object))
		for file in all_files:
			#print(file.folder.name +"\t"+file.file.name+"\t"+foldername)

			if file.folder == folder_object:
				path_val=[]
				string_val = ''
				original_value = file.folder
				if file.folder is not None:
					while file.folder.parentfolder is not None:
						path_val.append(file.folder.name)
						file.folder = file.folder.parentfolder
					path_val.append(file.folder.name)
					for i in range(len(path_val)-1,-1,-1):
						string_val = string_val + "/" + path_val[i]
					file.folder = original_value
					argument_val = string_val[1:]+'/'
				else:
					argument_val = ''

				file.delete()
				print("deleted file "+str(file.file.name))
				k.key = 'media/'+'userfiles/' + user_object.user.username + '/'+ argument_val + os.path.basename(file.file.name)
				print (k.key)
				b.delete_key(k)
		
		return_list=[]
		for item in all_folders:
			if item.parentfolder == folder_object:
				return_list.append(item.pk)
				return_list.append(item.name)

		return return_list

	def post(self,request):
		token = self.request.data['token']
		pk = self.request.data['id']
		name = self.request.data['object_name']
		r_val = self.request.data['r_value']
		env_flag = int(self.request.data['env_flag'])
		projectname = self.request.data['env_name']
		file_flag = 0 # 1 - file;0-not a file
		ref_fodler=None
		return_list=[]
		final_list =[]
		print (name,r_val)
		try:
			user_object = Token.objects.get(key=token)
			all_files = user_object.user.useruploadedfiles.all()
			all_folders = user_object.user.userfolders.all()
			if env_flag:
				if r_val == 'False':
					project_object = Projects.objects.get(name=projectname)
					project_files = ProjectFiles.objects.filter(project=project_object)
					file_object = None
					found = 0
					is_owner = 0
					for item in project_files: #check if file exists in projectFiles
						if os.path.basename(item.file_ref.file.name) == name:
							file_object = item.file_ref
							found = 1
							break

					if found:
						for item in all_files:
							if item == file_object:
								is_owner = 1
								break
					if found == 0:
						message = {'message':"File does not exist.",'status_code':404}
						return Response(message,status=404)
					if is_owner == 0:
						message = {'message':"Permission denied.",'status_code':404}
						return Response(message,status=404)
					if found and is_owner:
						project_files_object = ProjectFiles.objects.get(project=project_object,file_ref=file_object)
						project_files_object.delete()

						new_projectlogs_object = ProjectDetailsLogger(user=user_object.user,project=project_object,action=user_object.user.username + ' deleted '+ name)
						new_projectlogs_object.save()

						message = {'message':"File removed.",'status_code':204}
						return Response(message,status=204)
				else:
					project_object = Projects.objects.get(name=projectname)
					project_folders = ProjectFolders.objects.filter(project=project_object)
					folder_object = None
					found = 0
					is_owner = 0
					for item in project_folders: #check if file exists in projectFolders
						if os.path.basename(item.folder_ref.name) == name:
							folder_object = item.folder_ref
							found = 1
							break
					if found:
						for item in all_folders:
							if item == folder_object:
								is_owner = 1
								break
					if found == 0:
						message = {'message':"Directory does not exist.",'status_code':404}
						return Response(message,status=404)
					if is_owner == 0:
						message = {'message':"Permission denied.",'status_code':404}
						return Response(message,status=404)
					if found and is_owner:
						project_folder_object = ProjectFolders.objects.get(project=project_object,folder_ref=folder_object)
						project_folder_object.delete()
						
						new_projectlogs_object = ProjectDetailsLogger(user=user_object.user,project=project_object,action=user_object.user.username + ' deleted '+ name)
						new_projectlogs_object.save()

						message = {'message':"Directory removed.",'status_code':204}
						return Response(message,status=204)
			else:
				if pk!='':
					folder_object = user_object.user.userfolders.get(pk=int(pk))
				else:
					folder_object = None
				if r_val == 'False':
					for file in all_files:
						if file.folder == folder_object and os.path.basename(file.file.name) == name:
							file_flag = 1

							path_val=[]
							string_val = ''
							original_value = file.folder
							if file.folder is not None:
								while file.folder.parentfolder is not None:
									path_val.append(file.folder.name)
									file.folder = file.folder.parentfolder
								path_val.append(file.folder.name)
								for i in range(len(path_val)-1,-1,-1):
									string_val = string_val + "/" + path_val[i]
								file.folder = original_value
								argument_val = string_val[1:]+'/'
							else:
								argument_val = ''

							file.delete()
							k.key = 'media/'+'userfiles/' + user_object.user.username + '/'+ argument_val + os.path.basename(file.file.name)
							print (k.key)
							b.delete_key(k)
							message = {'message':"File deleted.",'status_code':204}
							return Response(message,status=204)
					ref_folder = None
					if file_flag == 0:
						for folder in all_folders:
							if folder.parentfolder == folder_object and folder.name == name:
								ref_folder = folder
								break
						if ref_folder is not None:
							folder_empty_flag = 1 # 1 is empty and 0 is non-empty
							for folder in all_folders:
								if folder.parentfolder == ref_folder:
									folder_empty_flag = 0
									break	
							if folder_empty_flag:
								for file in all_files:
									if file.folder == ref_folder:
										folder_empty_flag = 0
										break
							if folder_empty_flag:
								ref_folder.delete()
								message = {'message':'Folder deleted.','status_code':204}
								return Response(message,status=204)
							else:
								message = {'message':"ERROR: Directory is not empty.",'status_code':400}
								return Response(message,status=400)
						else:
							message = {'message':"ERROR: File does not exist.",'status_code':404}
							return Response(message,status=404)

				elif r_val=='True':
					for file in all_files:
						if file.folder == folder_object and os.path.basename(file.file.name) == name:
							file_flag = 1
							message = {'message':"ERROR: -r option is valid only with directories.",'status_code':400}
							return Response(message,status=400)
					ref_folder = None
					if file_flag == 0:
						#recursive delete
						for folder in all_folders:
							if folder.parentfolder == folder_object and folder.name == name:
								ref_folder = folder
								break
						if ref_folder is not None:
							#call delete function
							ref_folder_pk = ref_folder.pk
							ref_folder_name = ref_folder.name
							return_list = RemoveObjectView.remove_all_files_dirs(token,all_files,all_folders,ref_folder_pk,ref_folder_name)
							if return_list:
								#print(return_list)
								final_list.extend(return_list)
								n = len(return_list)
								i = 0
								while i < n:
								#for i in range(0,len(return_list),2):
									val = RemoveObjectView.remove_all_files_dirs(token,all_files,all_folders,return_list[i],return_list[i+1])
									if val:
										return_list.extend(val)
										final_list.extend(val)
										print(return_list,len(return_list))
									i = i + 2
									n = len(return_list)
							print("\n")
							print ("final_list"+str(final_list))
							# if final_list:
							# 	for i in range(0,len(final_list),2):
							# 		folder_object = user_object.user.userfolders.get(pk=int(final_list[i]))
							# 		print("deleting folder  " + folder_object.name+ "   "+str(folder_object.pk))
							# 		folder_object.delete()
							folder_object = user_object.user.userfolders.get(pk=int(ref_folder_pk))
							print("deleting folder  " + ref_folder_name+ "   "+str(ref_folder_pk))
							folder_object.delete()
							message = {'message':"Folder deleted.",'status_code':204}
							return Response(message,status=204)
							
						else:
							message = {'message':"ERROR: Directory does not exist.",'status_code':404}
							return Response(message,status=404)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)


class NewProjectView(APIView):
	def generate_rand(n):
		llimit = 10**(n-1)
		ulimit = (10**n)-1
		return random.randint(llimit,ulimit)

	def post(self,request):
		token = self.request.data['token']
		projectname = self.request.data['projectname']

		try:
			user_object = Token.objects.get(key=token)
			projectname = user_object.user.username + ':' + projectname
			
			#create project object
			new_project_object = Projects(name=projectname)
			new_project_object.save()
			
			#generate accesskey
			all_user_projects = user_object.user.userprojects.all()
			accesskey_list = []
			for item in all_user_projects:
				accesskey_list.append(item.access_key)

			num = NewProjectView.generate_rand(4)
			while num in accesskey_list:
				print("NEW")
				num = generate_rand(4)

			access_key = num
			print(access_key)
			#create userprojects object
			new_userprojects_object = UserProjects(user=user_object.user,project=new_project_object,status='A',access_key=access_key)
			new_userprojects_object.save()
			
			#add to logs
			new_projectlogs_object = ProjectDetailsLogger(user=user_object.user,project=new_project_object,action=user_object.user.username + ' created '+ projectname)
			new_projectlogs_object.save()
			## Format time stamp - time.strftime("[%d/%B/%Y %H:%M:%S]")
			print('created project and userproject object ' + str(new_userprojects_object.pk) + ' ' + new_project_object.name +' ' +str(new_project_object.pk) )
			data = {'projectname':new_project_object.name,'access_key':access_key}
			message = {'message':data,'status_code':200}
			return Response(message,status=200)
		except IntegrityError:
			#print("here")
			message = {'message':"Project exists.",'status_code':400}
			return Response(message,status=400)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)


class AddFileToProjectView(APIView):
	def post(self,request):
		token = self.request.data['token']
		projectname = self.request.data['projectname']
		filename = self.request.data['filename']
		pk = self.request.data['id']
		file_flag = 0
		try:
			user_object = Token.objects.get(key=token)
			all_files = user_object.user.useruploadedfiles.all()
			if pk!='':
				folder_object = user_object.user.userfolders.get(pk=int(pk))
			else:
				folder_object = None
			for item in all_files:
				if item.folder == folder_object and os.path.basename(item.file.name) == filename:
					file_object = item
					file_flag = 1
					break
			if file_flag:
				try:
					project_object = Projects.objects.get(name=projectname)
					new_projectfiles_object = ProjectFiles(project=project_object,file_ref=file_object)
					new_projectfiles_object.save()
					print('created projectfiles object ' + str(new_projectfiles_object.pk))
					return Response(status=204)
				except Projects.DoesNotExist:
					return Response(status=404)
			else:
				return Response(status=404)
		except Token.DoesNotExist:
			return Response(status=404)

class ListAllProjectsView(APIView):
	def post(self,request):
		token = self.request.data['token']
		try:
			return_val=[]
			user_object = Token.objects.get(key=token)
			all_projects = user_object.user.userprojects.all()
			for project in all_projects:
				if project.status == 'A':
					status = 'Admin'
				else:
					status = 'Contributor'
				return_val.append(project.project.name+"\t"+status+"\t"+str(project.access_key))
			message = {'message':return_val,'status_code':200}
			return Response(message,status=200)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)


class LoadProjectView(APIView):
	def post(self,request):
		token = self.request.data['token']
		projectid = int(self.request.data['projectid'])
		project_flag=0
		try:
			user_object = Token.objects.get(key=token)
			all_projects = user_object.user.userprojects.all()
			for project in all_projects:
				if project.access_key == projectid:
					project_flag=1
					data = {'projectname':project.project.name,'projectid':project.access_key}
					message = {'message':data,'status_code':200}
					print(message)
					return Response(message,status=200)
			if project_flag==0:
				message = {'message':"ERROR: Specified project does not exist in your antarin account",'status_code':404}
				return Response(message,status=404)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)


class ImportDataView(APIView):

	def find_folder(foldername,parentfolder,all_folders):
		folder_flag = 0
		for item in all_folders:
			if item.name == foldername and item.parentfolder == parentfolder:
				folder_object = item
				folder_flag = 1
				break
		if folder_flag == 0:
			return -1
		return folder_object

	def find_file(filename,parentfolder,all_files):
		file_flag = 0
		for item in all_files:
			if item.folder == parentfolder and os.path.basename(item.file.name) == filename:
				file_object = item
				file_flag = 1
				break
		if file_flag == 0:
			return -1
		return file_object

	def post(self,request):
		token = self.request.data['token']
		folder_flag = int(self.request.data['folder_flag'])
		projectname = self.request.data['env_name']
		path = self.request.data['path']
		error_flag = 0
		try:
			user_object = Token.objects.get(key=token)
			project_object = Projects.objects.get(name=projectname)
			if folder_flag:
				#FOLDER
				all_folders = user_object.user.userfolders.all()
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
					val = ImportDataView.find_folder(plist[0],parentfolder,all_folders)
					if val != -1:
						parentfolder = val
						print (parentfolder.name)
					else:
						message = {'message':"ERROR: Directory does not exist.",'status_code':404}
						return Response(message,status=404)
				else:
					for i in range(1,len(plist)):
						val = ImportDataView.find_folder(plist[i],parentfolder,all_folders)
						if val != -1:
							parentfolder = val
							print (parentfolder.name)
						else:
							message = {'message':"ERROR: Directory does not exist.",'status_code':404}
							return Response(message,status=404)
				folder_object = val
				all_projectfolders = ProjectFolders.objects.filter(project=project_object)
				for item in all_projectfolders:
					if item.folder_ref == folder_object:
						print("Duplicate folder ref")
						error_flag = 1
						break

				for item in all_projectfolders:
					if item.folder_ref.name == folder_object.name:
						print("Duplicate folder ref")
						error_flag = 1
						break

				if error_flag ==0:
					
					new_projectfolder_object = ProjectFolders(project=project_object,folder_ref=folder_object)
					print("Adding "  + new_projectfolder_object.folder_ref.name + " to " + new_projectfolder_object.project.name)
					new_projectfolder_object.save()

					new_projectlogs_object = ProjectDetailsLogger(user=user_object.user,project=project_object,action=user_object.user.username + ' added directory '+ new_projectfolder_object.folder_ref.name)
					new_projectlogs_object.save()

					message = {'message':'Imported directory.','status_code':204}
					return Response(message,status=204)
				else:
					message = {'message':"ERROR: Directory exists.",'status_code':404}
					return Response(message,status=404)
			else:
				#FILE
				
				all_folders = user_object.user.userfolders.all()
				all_files = user_object.user.useruploadedfiles.all()

				plist = path
				plist = plist.split('/')
				if path[0]=='/':
				    plist = plist[1:]
				
				print (plist)
				parentfolder = None
				val = None
				for i in range(1,len(plist)-1):
					print(plist[i],parentfolder)
					val = ImportDataView.find_folder(plist[i],parentfolder,all_folders)
					if val != -1:
						parentfolder = val
						print(parentfolder.name)
					else:
						message = {'message':"ERROR: Path specified is not correct.",'status_code':404}
						return Response(message,status=404)
				folder_object = val
				file_object = ImportDataView.find_file(plist[-1],folder_object,all_files)
				if file_object != -1:
					all_projectfiles = ProjectFiles.objects.filter(project=project_object)
					for item in all_projectfiles:
						if item.file_ref == file_object:
							print("duplicate ref")
							error_flag = 1
							break

					for item in all_projectfiles:
						if os.path.basename(item.file_ref.file.name) == os.path.basename(file_object.file.name):
							print("duplicate ref")
							error_flag = 1
							break
					
					if error_flag == 0:
						
						new_projectfile_object = ProjectFiles(project=project_object,file_ref=file_object)
						print("Adding " + new_projectfile_object.file_ref.file.name + " to " + new_projectfile_object.project.name)
						new_projectfile_object.save()

						new_projectlogs_object = ProjectDetailsLogger(user=user_object.user,project=project_object,action=user_object.user.username + ' added file '+ os.path.basename(new_projectfile_object.file_ref.file.name))
						new_projectlogs_object.save()

						message = {'message':'Imported file.','status_code':204}
						return Response(message,status=204)
					else:
						print("here")
						message = {'message':"ERROR: File exists.",'status_code':404}
						return Response(message,status=404)
				else:
					message = {'message':"ERROR: File does not exist.",'status_code':404}
					return Response(message,status=404)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)


class AddContributorView(APIView):

	def generate_rand(n):
		llimit = 10**(n-1)
		ulimit = (10**n)-1
		return random.randint(llimit,ulimit)


	def post(self,request):
		token = self.request.data['token']
		projectname = self.request.data['env_name']
		username = self.request.data['username']
		try:
			user_object = Token.objects.get(key=token)
			project_object = Projects.objects.get(name=projectname)
			user_project_object = user_object.user.userprojects.get(project=project_object)
			all_userprojects = UserProjects.objects.all()
			error_flag=0 #0-new contributor object

			if user_project_object.status!='C':
				try:
					contributor_obj = User.objects.get(username=username)
					for projects in all_userprojects:
						print(project_object.pk ,projects.project.pk,projects.user.pk,projects.user.username,contributor_obj.pk,contributor_obj.username)
						if projects.project == project_object and projects.user == contributor_obj:
							error_flag=1
							print("here" )
							break
					if error_flag==0 :

						all_user_projects = contributor_obj.userprojects.all()
						accesskey_list = []
						for item in all_user_projects:
							accesskey_list.append(item.access_key)

						num = NewProjectView.generate_rand(4)
						while num in accesskey_list:
							num = generate_rand(4)

						access_key = num
						print(access_key)

						new_userprojects_object = UserProjects(user=contributor_obj,project=project_object,status='C',access_key=access_key)
						new_userprojects_object.save()
						print("Added " + new_userprojects_object.user.username + " as contributor to "+ new_userprojects_object.project.name  )
						
						new_projectlogs_object = ProjectDetailsLogger(user=user_object.user,project=project_object,action=user_object.user.username + ' added '+ new_userprojects_object.user.username + ' as contributor.' )
						new_projectlogs_object.save()

						data = {'user':new_userprojects_object.user.username,'acess_key':access_key}
						message = {'message':data,'status_code':200}
						return Response(message,status=200)
					else:
						message = {'message':"ERROR: Specified user is already a contributor to this project",'status_code':404}
						return Response(message,status=404)					
				except User.DoesNotExist:
					message = {'message':"ERROR: Could not find an Antarin user with the specified username",'status_code':404}
					return Response(message,status=404)
			else:
				print("permission denied")
				message = {'message':"ERROR: Permission denied",'status_code':404}
				return Response(message,status=404)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)


class DeleteProjectView(APIView):
	def get(self,request):
		token = self.request.data['token']
		projectid = self.request.data['projectid']
		try:
			user_object = Token.objects.get(key=token)
			#project_object = Projects.objects.get(name=projectname)
			user_project_object = user_object.user.userprojects.get(access_key=projectid)
			if user_project_object.status != 'A':
				print("Permission denied.")
				message = {'message':'Permission denied.','status_code':400}
				return Response(message,status=400)
			else:
				print("'Is an Admin. Has permissions to delete project.'")
				message = {'message':'Is an Admin. Has permissions to delete project.','status_code':200}
				return Response(message,status=200)
		except UserProjects.DoesNotExist:
			message = {'message':'You are not a part of this project. Permission denied','status_code':400}
			return Response(message,status=400)
		# except Projects.DoesNotExist:
		# 	message = {'message':'Project does not exist.','status_code':404}
		# 	return Response(message,status=404)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)

	def post(self,request):
		token = self.request.data['token']
		projectid = self.request.data['projectid']
		password = self.request.data['pwd']
		try:
			user_object = Token.objects.get(key=token)
			username = user_object.user.username
			user_val = User.objects.get(username__exact=username)
			#print (password)
			if user_val.check_password(password):
				print("correct password")
				user_project_object = user_object.user.userprojects.get(access_key=projectid)
				project_object = user_project_object.project
				project_object.delete()
				print("deleted project")
				
				# new_projectlogs_object = ProjectDetailsLogger(user=user_object.user,project=project_object,action=user_object.user.username + ' deleted project. ' )
				# new_projectlogs_object.save()
				
				message = {'message':'Project deleted.','status_code':200}
				return Response(message,status=404)
			else:
				print('incorrect password')
				message = {'message':'Invalid password.','status_code':404}
				return Response(message,status=404)
		# except Projects.DoesNotExist:
		# 	message = {'message':'Project does not exist.','status_code':404}
		# 	return Response(message,status=404)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)

class LeaveProjectView(APIView):
	def post(self,request):
		token = self.request.data['token']
		projectid = self.request.data['projectid']
		try:
			user_object = Token.objects.get(key=token)
			#project_object = Projects.objects.get(name=projectname)
			user_project_object = user_object.user.userprojects.get(access_key=projectid)
			project_object = user_project_object.project
			if user_project_object.status == 'A':
				message = {'message':'Permission denied.','status_code':400}
				return Response(message,status=400)
			else:
				user_project_object.delete()

				new_projectlogs_object = ProjectDetailsLogger(user=user_object.user,project=project_object,action=user_object.user.username + ' left project. ' )
				new_projectlogs_object.save()

				message = {'message':'Project record deleted from user account.','status_code':200}
				return Response(message,status=200)
		except UserProjects.DoesNotExist:
			message = {'message':'You are not a part of this project. Permission denied','status_code':400}
			return Response(message,status=400)
		# except Projects.DoesNotExist:
		# 	message = {'message':'Project does not exist.','status_code':404}
		# 	return Response(message,status=404)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)


class CheckLogsView(APIView):
	def post(self,request):
		token = self.request.data['token']
		projectname = self.request.data['env_name']
		try:
			user_object = Token.objects.get(key=token)
			project_object = Projects.objects.get(name=projectname)
			all_logs = ProjectDetailsLogger.objects.filter(project=project_object)
			return_val = []
			for item in all_logs:
				logs = []
				logs.append(item.timestamp.strftime("[%d/%B/%Y %H:%M:%S]"))
				logs.append(item.action)
				return_val.append(logs)
			message = {'message': return_val,'status_code':200}
			return Response(message,status=200)
		except Projects.DoesNotExist:
			message = {'message':'Project does not exist.','status_code':404}
			return Response(message,status=404)
		except Token.DoesNotExist:
			message = {'message':'Session token is not valid.','status_code':404}
			return Response(message,status=404)



# class DownloadFileView(APIView):
# 	def get(self,request):
# 		conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
# 		bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
# 		bucket_list = bucket.list()
# 		key = bucket.get_key('media/user_files/'+request.data['file'].strip('"'))
# 		filepath = os.path.join("/Users/ruchikashivaswamy/", request.data['file'].strip('"'))
# 		key.get_contents_to_filename(filepath)
# 		file = open(filepath)
# 		response = HttpResponse(FileWrapper(file), content_type='application/text')
# 		return response
				

# class DeleteFileView(APIView):
# 	def post(self,request,format=None):
# 		token = request.data['token'].strip('"')
# 		filename = request.data['file'].strip('"')
# 		print(token,filename)
# 		user_val = Token.objects.get(key=token)
# 		if 'userfiles/' not in filename:
# 			filename = 'userfiles/' + user_val.user.username + '/'+ filename
# 		print(filename)
# 		file = user_val.user.useruploadedfiles.filter(file=filename).first()
# 		file.delete() 

# 		conn = S3Connection(settings.AWS_ACCESS_KEY_ID , settings.AWS_SECRET_ACCESS_KEY)
# 		b = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
# 		k = Key(b)
# 		k.key = 'media/'+filename
# 		print(k.key)
# 		b.delete_key(k)
# 		return Response(status=204)
