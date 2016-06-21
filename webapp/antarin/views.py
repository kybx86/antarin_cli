from django.shortcuts import render_to_response, get_object_or_404,render
from antarin.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
import hashlib,random
from antarin.models import UserProfile
from django.utils import timezone

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
			#print(type(keyval))
			#print(type(usernamekey))
			userdata['activation_key'] = hashlib.sha1(keyval+usernamekey).hexdigest()
			#userdata['email_path'] = "activationEmail.html"
			userdata['email_subject'] = "[Antarin] Please verify your email address"
			print(userdata)
			form.sendEmail(userdata)
			form.save(userdata)
			return HttpResponseRedirect('./success')
	else:
		form = RegistrationForm()
	variables = RequestContext(request,{'form':form})
	return render_to_response('registration/signup.html',variables,)

def activation(request,key):
	print(key)
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

def signup_success(request):
	return render_to_response('registration/success.html',)

@login_required
def userHomepage(request):
	if request.method == 'GET':
		if request.GET.get('num1') and request.GET.get('num2'):
			num1 = int(request.GET.get('num1'))
			num2 = int(request.GET.get('num2'))
			sum = calculate_sum(num1,num2)
			variables = RequestContext(request,{'user':request.user,'sum':sum})	
		else:
			variables = RequestContext(request,{'user':request.user})	
	return render_to_response('home.html',variables)	

def calculate_sum(num1,num2):
    return num1+num2
