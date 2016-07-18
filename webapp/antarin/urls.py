#AUTHOR : RUCHIKA SHIVASWAMY
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
from rest_framework.authtoken import views

urlpatterns = [
	url(r'^$', antarin_views.login_view),
	url(r'^accounts/login/?$',antarin_views.login_view),
	url(r'^logout/$',auth_views.logout_then_login),
	url(r'^signup/$', antarin_views.signup),
	url(r'^signup/success/$',antarin_views.signup_success),
	url(r'^home/$',antarin_views.userHomepage, name = "user_homepage"),
	url(r'^activate/(?P<key>.+)$', antarin_views.activation),
	#url(r'^new-activation-link/(?P<user_id>\d+)/$', antarin_views.new_activation_link),
	url(r'passwordreset/$', antarin_views.password_reset),
	url(r'^passwordreset/success/$',antarin_views.password_reset_success),
	url(r'^passwordreset/activation/(?P<key>.+)$', antarin_views.password_key_activation),
	url(r'^passwordreset/redirect/$', antarin_views.password_reset_redirect),
	url(r'^rest-auth/', include('rest_auth.urls')),
	url(r'^rest-summary/',antarin_views.UserSummaryView.as_view()),
	url(r'^rest-ls/',antarin_views.ListFilesView.as_view()),
	url(r'^rest-fileupload/$',antarin_views.UploadFileView.as_view()),
	url(r'^rest-filedelete/$',antarin_views.DeleteFileView.as_view()),
	url(r'^rest-filedownload/',antarin_views.DownloadFileView.as_view()),
	url(r'^rest-logout/$',antarin_views.LogoutView.as_view()),
	url(r'^rest-mkdir/$',antarin_views.CreateDirectoryView.as_view()),
	url(r'^rest-cd/$',antarin_views.ChangeDirectoryView.as_view()),
	url(r'^rest-pwd/$',antarin_views.CurrentWorkingDirectoryView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

