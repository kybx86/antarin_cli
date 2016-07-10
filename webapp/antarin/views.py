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
from antarin.models import UserProfile,UserUploadedFiles
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

#from django.core.servers.basehttp import FileWrapper
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

class ListFilesView(APIView):
	def get(self,request):
		try:
			user_val = Token.objects.get(key = self.request.data)
			all_files = user_val.user.useruploadedfiles.all()
			return_val = [file.file.name for file in all_files]
			print(return_val)
			return Response(return_val)
		except Token.DoesNotExist:
			return None
		
class UploadFileView(APIView):
	#parser_classes = (FileUploadParser,)
	def put(self, request, filename, format=None):
		file_object = request.data['file']
		print (request.data)
		token = request.data['token'].strip('"')
		print(token)

		user_val = Token.objects.get(key = token)
		user_files = UserUploadedFiles()
		user_files.user = user_val.user
		user_files.file = file_object
		print(user_val.user.userprofile.data_storage_used)

		all_files = user_val.user.useruploadedfiles.all()
		used_data_storage = calculate_used_data_storage(all_files)
		user_val.user.userprofile.data_storage_used = str(used_data_storage)
		user_val.user.save()
		user_val.user.userprofile.save()
		user_files.save()
		print("Success!")
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
	def post(self,request,filename,format=None):
		token = request.data['token'].strip('"')
		filename = request.data['file'].strip('"')
		print(token,filename)
		user_val = Token.objects.get(key=token)
		if 'user_files/' not in filename:
			filename = 'user_files/' + filename
		file = user_val.user.useruploadedfiles.filter(file=filename).first()
		file.delete() 
		return Response(status=204)

class UserSummaryView(APIView):
	def get(self,request):
		try:
			user_val = Token.objects.get(key = self.request.data)
			user_data = (user_val.user.first_name,user_val.user.last_name,user_val.user.username,user_val.user.userprofile.total_data_storage,user_val.user.userprofile.data_storage_used)
			#print(return_val)
			return Response(user_data)
		except Token.DoesNotExist:
			return None
