import re
import datetime
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

class CustomizedAuthenticationForm(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(CustomizedAuthenticationForm, self).__init__(*args, **kwargs)
		self.base_fields['username'].widget.attrs['placeholder'] = 'Email'
		self.base_fields['password'].widget.attrs['placeholder'] = 'Password'

class RegistrationForm(forms.Form):
	username = forms.RegexField(regex = r'^\w+$', 
		widget = forms.TextInput(attrs=dict(reuired=True,max_length=20)), 
		label=_("Username"), 
		error_messages = {'invalid' : _("This field can take only letters,numbers and underscores.")})
	email = forms.EmailField(widget=forms.TextInput(attrs = dict(required=True,max_length=30)), label=_("Email Address"))
	password1 = forms.CharField(widget = forms.PasswordInput(attrs=dict(required = True, max_length=20, render_value=False)),label = _("Password"))
	password2 = forms.CharField(widget = forms.PasswordInput(attrs=dict(required = True, max_length=20, render_value=False)),label = _("Password entered again"))

	#to ensure usernames being stored in the databases are unique
	def clean_username(self):
		try:
			user = User.objects.get(username__iexact = self.cleaned_data['username'])
		except User.DoesNotExist:
			return self.cleaned_data['username']
		raise forms.ValidationError(_("This username already exits. Please try another one."))

	# check if password1 and password2 match
	def clean(self):
		if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password1'] != self.cleaned_data['password2']:
				raise forms.ValidationError(_("The two password fields did not match. Please try again."))
		return self.cleaned_data

class calculateAgeForm(forms.Form):
	dateofbirth = forms.DateField(initial=datetime.date.today,label=_("Date of Birth"))