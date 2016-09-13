#AUTHOR : RUCHIKA SHIVASWAMY
from django.conf.urls import url,include
from django.contrib import admin

urlpatterns = [
	url(r'^', include('antarin.urls')),
    url(r'^admin/', admin.site.urls),
]
