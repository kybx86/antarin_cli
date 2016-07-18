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
from datetime import datetime
import hashlib,random,json,boto,os
from antarin.models import UserProfile,UserUploadedFiles,UserFolder
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
			userdata['email_subject'] = "[Antarin] Please verify your email address"
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
			userdata['email_subject'] = "[Antarin] Reset your Password "
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
			user_files.folder = NONE
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
		list_val = []
		try:
			user_object = Token.objects.get(key = token)
			#print(token,pk)
			if pk != "":
				folder_object = user_object.user.userfolders.get(pk=int(pk))
			else:
				folder_object = None
			
			for file in user_object.user.useruploadedfiles.all():
				#print (file.file.name,file.folder)
				if file.folder == folder_object:
					list_val.append(os.path.basename(file.file.name))
			
			for folder in user_object.user.userfolders.all():
				if folder.parentfolder == folder_object:
					list_val.append("/"+folder.name)
			return Response(list_val)
		except Token.DoesNotExist:
			return Response(status=404)
		
class UploadFileView(APIView):
	#parser_classes = (FileUploadParser,)
	def put(self, request,format=None):
		file_object = request.data['file']
		print (request.data)
		token = request.data['token'].strip('"')
		#print(token)
		pk = request.data['id_val'].strip('"')
		user_val = Token.objects.get(key = token)
		folder_object = user_val.user.userfolders.get(pk=int(pk))
		user_files = UserUploadedFiles()
		user_files.user = user_val.user
		user_files.file = file_object
		user_files.folder = folder_object
		print(user_val.user.userprofile.data_storage_used)

		all_files = user_val.user.useruploadedfiles.all()
		used_data_storage = calculate_used_data_storage(all_files)
		user_val.user.userprofile.data_storage_used = str(used_data_storage)
		user_val.user.save()
		user_val.user.userprofile.save()
		user_files.save()
		#print("Success!")
		print(user_val.user.userprofile.data_storage_used)
		#catch error when save didn't work fine and return status 400
		return Response(status=204)

class DownloadFileView(APIView):
	def get(self,request):
		conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
		bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
		bucket_list = bucket.list()
		key = bucket.get_key('media/user_files/'+request.data['file'].strip('"'))
		filepath = os.path.join("/Users/ruchikashivaswamy/", request.data['file'].strip('"'))
		key.get_contents_to_filename(filepath)
		file = open(filepath)
		response = HttpResponse(FileWrapper(file), content_type='application/text')
		return response
				

class DeleteFileView(APIView):
	def post(self,request,format=None):
		token = request.data['token'].strip('"')
		filename = request.data['file'].strip('"')
		print(token,filename)
		user_val = Token.objects.get(key=token)
		if 'userfiles/' not in filename:
			filename = 'userfiles/' + user_val.user.username + '/'+ filename
		print(filename)
		file = user_val.user.useruploadedfiles.filter(file=filename).first()
		file.delete() 

		conn = S3Connection(settings.AWS_ACCESS_KEY_ID , settings.AWS_SECRET_ACCESS_KEY)
		b = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
		k = Key(b)
		k.key = 'media/'+filename
		print(k.key)
		b.delete_key(k)
		return Response(status=204)

class UserSummaryView(APIView):
	def get(self,request):
		try:
			user_val = Token.objects.get(key = self.request.data)
			user_data = (user_val.user.first_name,user_val.user.last_name,user_val.user.username,user_val.user.userprofile.total_data_storage,user_val.user.userprofile.data_storage_used)
			print(Response(user_data))
			return Response(user_data)
		except Token.DoesNotExist:
			return None


class LogoutView(APIView):
	def post(self,request):
		try:
			instance = Token.objects.get(key=self.request.data['token'])
			instance.delete()
			return Response(status=204)
		except Token.DoesNotExist:
			return Response(status=404)

class CreateDirectoryView(APIView):
	def post(self,request):
		token = self.request.data['token']
		foldername = self.request.data['foldername']
		pk = self.request.data['id']
		try:
			user_object = Token.objects.get(key = token)
			if pk != "":
				folder_object = user_object.user.userfolders.get(pk=int(pk))
			else:
				folder_object = None
			new_folder_object = UserFolder(user=user_object.user,name=foldername,parentfolder=folder_object)
			new_folder_object.save()
			return Response(status=204)
		except Token.DoesNotExist:
			return Response(status=404)

class ChangeDirectoryView(APIView):
	def post(self,request):
		flag = 0
		token = self.request.data['token']
		foldername = self.request.data['foldername']
		pk = self.request.data['id']
		try:
			user_object = Token.objects.get(key=token)
			if pk != "":
				folder_object = user_object.user.userfolders.get(pk=int(pk))
			else:
				folder_object = None
			if foldername == '..':
				if folder_object.parentfolder is not None:
					current_directory = folder_object.parentfolder.name
					id_val = folder_object.parentfolder.pk
				else:
					current_directory = "/"
					id_val = ""
				data = {'current_directory':current_directory,'id':id_val}
				return Response(json.dumps(data))
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
					return Response(json.dumps(data))
				else:
					return Response(status=404)
		except Token.DoesNotExist:
			return Response(status=404)


class CurrentWorkingDirectoryView(APIView):
	def post(self,request):
		token = self.request.data['token']
		pk = self.request.data['id']
		try:
			user_object = Token.objects.get(key=token)
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
				print(string_val)
				return Response(json.dumps(string_val))
			else:
				folder_object = None
				return Response(json.dumps('/'))
		except Token.DoesNotExist:
			return Response(status=404)


