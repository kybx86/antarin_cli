import re
import datetime
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django.utils.safestring import mark_safe

class CustomizedAuthenticationForm(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(CustomizedAuthenticationForm, self).__init__(*args, **kwargs)
		self.base_fields['username'].widget.attrs['placeholder'] = 'Email'
		self.base_fields['password'].widget.attrs['placeholder'] = 'Password'

class RegistrationForm(forms.Form):
	firstname = forms.CharField(widget = forms.TextInput(attrs=dict(required=True,max_length=30,placeholder = 'Firstname')))
	lastname = forms.CharField(widget = forms.TextInput(attrs=dict(required=True,max_length=30,placeholder = 'Lastname')))
	username = forms.EmailField(widget = forms.TextInput(attrs=dict(required=True,max_length=30,placeholder='Email')))
	password = forms.CharField(help_text= "must be atleast six characters in length and contain letters and numbers",widget = forms.PasswordInput(attrs=dict(required = True, max_length=20,placeholder = 'Password',render_value=False)))

	#to ensure usernames being stored in the databases are unique
	def clean_username(self):
		try:
			user = User.objects.get(username__iexact = self.cleaned_data['username'])
		except User.DoesNotExist:
			return self.cleaned_data['username']
		raise forms.ValidationError(_(mark_safe('Account with this email address already exists. <br/> <a href="/" id="email_error">Log In?</a>')))
		
	def clean_password(self):
		password = str(self.cleaned_data.get('password'))
		if len(password) < 6 or any(char.isdigit() for char in password)==False or any(char.isalpha() for char in password)==False:		
			raise forms.ValidationError(_(mark_safe('Password does not meet requirements, <br/> Please try again')))
		return self.cleaned_data['password']

	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)
		for fieldname in ['firstname','lastname','username','password']:
			self.fields[fieldname].label = ''