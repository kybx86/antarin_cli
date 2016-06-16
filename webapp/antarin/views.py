from django.shortcuts import render_to_response
from antarin.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from datetime import datetime

@csrf_protect
def signup(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(
				username = form.cleaned_data['username'],
				password = form.cleaned_data['password1'],
				email    = form.cleaned_data['email']
				)
			return HttpResponseRedirect('./success')
	else:
		form = RegistrationForm()
	variables = RequestContext(request,{'form':form})
	return render_to_response('registration/signup.html',variables,)

def signup_success(request):
	return render_to_response('registration/success.html',)

#def logout(request):
#	logout(request)
#	return HttpResponseRedirect('./success')

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
