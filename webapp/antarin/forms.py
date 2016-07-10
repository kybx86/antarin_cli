#AUTHOR : RUCHIKA SHIVASWAMY
'''
This file contains all forms used for 'antarin' application
'''

import datetime
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template import Context,Template
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from django.contrib.auth import authenticate
from antarin.models import UserProfile,UserUploadedFiles

'''
Custom login form with two form fields - username(is an emailField) and password
'''
class AuthenticationForm(forms.Form):
	username = forms.EmailField(widget = forms.TextInput(attrs=dict(required=True,placeholder="Email")))
	password = forms.CharField(widget = forms.PasswordInput(attrs = dict(required=True,placeholder="Password")))

	'''
	This method is called during the instantiation of AuthenticationForm class which happens in its corresponding view.
	By the time method clean() is called, the dictionary self.cleaned_data will be populated with form fields values. If a form field 
	did not meet validation requirements, then that particular key will not exist in the self.cleaned_data dictionary.
	This method therefore checks if both fields are validated and if yes, it proceeds to authenticate the user with the entered credentials. On authentication, if a 
	particular user is marked inactive then a validation error is raised. If form fields are not validated then a corresponding form validation error is raised.
	'''
	def clean(self):
		if 'username' in self.cleaned_data and 'password' in self.cleaned_data:
			username = self.cleaned_data['username'].lower()
			print(self.cleaned_data['username'].lower())
			password = self.cleaned_data['password']
			user = authenticate(username=username,password=password)
			if not user or not user.is_active:
				raise forms.ValidationError(_(mark_safe('Invalid email or password,<br/>please try again')))
			return self.cleaned_data
		elif 'username' not in self.cleaned_data:
			raise forms.ValidationError(_(mark_safe('Please enter a valid email address.')))
		elif 'password' in self.cleaned_data:
			raise forms.ValidationError(_(mark_safe('Please enter a valid password')))
		
	'''
	This method is called from its corresponding view only when the form submitted had no validation errors raised. It then authenticated the user and returns the respective user object.
	'''
	def login(self,request):
		username = self.cleaned_data['username'].lower()
		password = self.cleaned_data['password']
		user = authenticate(username=username,password=password)
		return user
'''
Custom registration form with four form fields - firstname,lastname,username(is an emailField) and password
'''
class RegistrationForm(forms.Form):
	firstname = forms.CharField(widget = forms.TextInput(attrs=dict(required=True,max_length=30,placeholder = 'First name')))
	lastname = forms.CharField(widget = forms.TextInput(attrs=dict(required=True,max_length=30,placeholder = 'Last name')))
	username = forms.EmailField(widget = forms.TextInput(attrs=dict(required=True,max_length=30,placeholder='Email')))
	password = forms.CharField(help_text= "must be atleast six characters in length and contain letters and numbers",widget = forms.PasswordInput(attrs=dict(required = True, max_length=20,placeholder = 'Password',render_value=False)))

	'''This method ensures the usernames being stored in the User database is unique and a validation error is raised otherwise'''
	def clean_username(self):
		try:
			user = User.objects.get(username__iexact = self.cleaned_data['username'].lower())
		except User.DoesNotExist:
			return self.cleaned_data['username'].lower()
		raise forms.ValidationError(_(mark_safe('Account with this email address already exists. <br/> <a href="/" id="email_error">Log In?</a>')))
	
	'''
	This method takes care of password validation and checks if the user entered password meets all specified requirements(must be 
	six characters long and contain atleast one number and letter); raises a validation error otherwise
	'''
	def clean_password(self):
		password = str(self.cleaned_data.get('password'))
		if len(password) < 6 or any(char.isdigit() for char in password)==False or any(char.isalpha() for char in password)==False:		
			raise forms.ValidationError(_(mark_safe('Password does not meet requirements, <br/> Please try again')))
		return self.cleaned_data['password']

	'''
	This method saves all the userdata that it receives in the form of a dictionary, to the User database.
	'''
	def save(self,userdata):
		user = User.objects.create_user(
				username = userdata['username'],
				password = userdata['password'],
				)
		user.first_name = userdata['firstname']
		user.last_name = userdata['lastname']
		user.is_active = False
		user.total_data_storage = '5 GB'
		user.save()

		user_profile = UserProfile()
		user_profile.user = user
		user_profile.activation_key = userdata['activation_key']
		user_profile.key_expires = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1), "%Y-%m-%d %H:%M:%S")
		user_profile.password_reset_key = ""
		user_profile.save()

	'''
	This method takes care of sending an email to the user entered email address on registration.
	'''
	def sendEmail(self,userdata):
		url = "/" + userdata['activation_key']
		context = Context({'activation_url':url,'firstname':userdata['firstname']})
		template = get_template('activationEmail.html')
		email_message = template.render(context)
		send_mail(userdata['email_subject'],email_message,'Antarin Technologies<noreply@antarintechnolgies.com>',[userdata['username']],fail_silently = False)

	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)
		for fieldname in ['firstname','lastname','username','password']:
			self.fields[fieldname].label = ''

'''
Custom Password reset form with one field - username(Email)
'''
class PasswordResetForm(forms.Form):
	username = forms.EmailField(widget = forms.TextInput(attrs=dict(required=True,placeholder="Email")))

	'''
	Validating the form fields by checking if the form field meets validation requirements and then fetching the corresponding user from thr User database.
	Validation errors are raised if conditions are not met.
	'''
	def clean(self):
		if 'username' in self.cleaned_data:
			if User.objects.filter(username = self.cleaned_data['username'].lower()).exists():
				return self.cleaned_data
			else:
				raise forms.ValidationError(_(mark_safe('Account with this email address does not exist. Please try again')))
		else:
			raise forms.ValidationError(_(mark_safe('Please enter a valid email address')))
		
	'''
	To retrieve firstname of user from User db when given his username
	'''
	def getFirstname(self,username):
		user = User.objects.get(username = username)
		return user.first_name

	'''
	To save the generated password key in the userprofile of corresponding user
	'''
	def save(self,userdata):
		user = User.objects.get(username = userdata['username'])
		user.userprofile.password_reset_key = userdata['password_reset_key']
		user.userprofile.save()

	'''
	To send an email to the user with password reset key
	'''
	def sendEmail(self,userdata):
		url = "/" + userdata['password_reset_key']
		context = Context({'activation_url':url,'firstname':userdata['firstname']})
		template = get_template('passwordResetEmail.html')
		email_message = template.render(context)
		send_mail(userdata['email_subject'],email_message,'Antarin Technologies<noreply@antarintechnolgies.com>',[userdata['username']],fail_silently = False)


'''
Password entry form where the user gets to enter his new password and confirm the same. Two fields - both password fields
'''
class PasswordEntryForm(forms.Form):
	password1 = forms.CharField(help_text= "must be atleast six characters in length and contain letters and numbers",widget = forms.PasswordInput(attrs=dict(required = True, max_length=20,placeholder = 'New Password',render_value=False)))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True,max_length=20,placeholder="Confirm Password",render_value=False)))
	#keyval = forms.CharField(widget = forms.HiddenInput())

	'''
	Validating password1 field - to check if the entered password meets all password requirements(must be six characters long and contain atleast
	 one number and letter);
	'''
	def clean_password1(self):
		password = str(self.cleaned_data.get('password1'))
		if len(password) < 6 or any(char.isdigit() for char in password)==False or any(char.isalpha() for char in password)==False:		
			print("password1 does not meet requirements")
			raise forms.ValidationError(_(mark_safe('Password does not meet requirements, <br/> Please try again')))
		print("password1 meets requirements")
		return self.cleaned_data['password1']	

	'''
	Validating password2 field - to check if the entered password matches with password1
	'''
	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password1 != password2:
			raise forms.ValidationError("Your passwords do not match")

class FileUploadForm(forms.ModelForm):
	class Meta:
		fields = ('file',)
		model = UserUploadedFiles

	def __init__(self, *args, **kwargs):
		super(FileUploadForm, self).__init__(*args, **kwargs)
		for fieldname in ['file']:
			self.fields[fieldname].label = ''
			self.fields[fieldname].widget = forms.HiddenInput()













