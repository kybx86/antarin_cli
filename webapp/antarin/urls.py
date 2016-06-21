'''
This file contains a mapping of different URLs to their respective views that are defined in views.py. The URLs defined here
are for 'antarin' application specifically. This urlconf is included in the main urls.py file of the project folder - webapp.
'''

from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from antarin import views as antarin_views
from antarin import forms as antarin_forms

urlpatterns = [
	url(r'^$', antarin_views.login_view),
	url(r'^accounts/login/?$',antarin_views.login_view),
	url(r'^logout/$',auth_views.logout_then_login),
	url(r'^signup/$', antarin_views.signup),
	url(r'^signup/success/$',antarin_views.signup_success),
	url(r'^home/$',antarin_views.userHomepage),
	url(r'^activate/(?P<key>.+)$', antarin_views.activation),
	#url(r'^new-activation-link/(?P<user_id>\d+)/$', antarin_views.new_activation_link),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

