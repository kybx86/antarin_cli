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
from antarin.models import UserProfile

'''
Custom login form with two form fields - username(is an emailField) and password
'''
class AuthenticationForm(forms.Form):
	username = forms.EmailField(widget = forms.TextInput(attrs=dict(required=True,placeholder="Email")))
	password = forms.CharField(widget = forms.PasswordInput(attrs = dict(required=True,placeholder="Password")))

	'''
	This method takes care of validating the different form fields - username and password, using Django's built-in
	methods and classes for form validation. A validation error is raised if the username and password entries do not match or
	if the user is inactive
	'''
	def clean(self):
		username = self.cleaned_data['username']
		password = self.cleaned_data['password']
		user = authenticate(username=username,password=password)
		if not user or not user.is_active:
			raise forms.ValidationError(_(mark_safe('Invalid email or password,<br/>please try again')))
		return self.cleaned_data

	def login(self,request):
		username = self.cleaned_data['username']
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
			user = User.objects.get(username__iexact = self.cleaned_data['username'])
		except User.DoesNotExist:
			return self.cleaned_data['username']
		raise forms.ValidationError(_(mark_safe('Account with this email address already exists. <br/> <a href="/" id="email_error">Log In?</a>')))
	
	'''This method takes care of password validation and checks if the user entered password meets all specified requirements(must be 
	six characters long and contain atleast one number and letter); raises a validation error otherwise'''
	def clean_password(self):
		password = str(self.cleaned_data.get('password'))
		if len(password) < 6 or any(char.isdigit() for char in password)==False or any(char.isalpha() for char in password)==False:		
			raise forms.ValidationError(_(mark_safe('Password does not meet requirements, <br/> Please try again')))
		return self.cleaned_data['password']

	def save(self,userdata):
		user = User.objects.create_user(
				username = userdata['username'],
				password = userdata['password'],
				)
		user.first_name = userdata['firstname']
		user.last_name = userdata['lastname']
		user.is_active = False
		user.save()

		user_profile = UserProfile()
		user_profile.user = user
		user_profile.activation_key = userdata['activation_key']
		user_profile.key_expires = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1), "%Y-%m-%d %H:%M:%S")
		user_profile.save()

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

