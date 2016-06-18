from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from antarin import views as antarin_views
from antarin import forms as antarin_forms

urlpatterns = [
	url(r'^$', auth_views.login,{'template_name':'registration/login.html','authentication_form':antarin_forms.CustomizedAuthenticationForm}),
	url(r'^accounts/login/?$',auth_views.login),
	url(r'^logout/$',auth_views.logout_then_login),
	url(r'^signup/$', antarin_views.signup),
	url(r'^signup/success/$',antarin_views.signup_success),
	url(r'^home/$',antarin_views.userHomepage),
]
