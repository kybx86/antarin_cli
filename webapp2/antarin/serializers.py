#AUTHOR : RUCHIKA SHIVASWAMY

from rest_framework import serializers
from antarin.models import UserUploadedFiles

class FetchFilesSerializer(serializers.ModelSerializer):
	#token = serializers.CharField(required=True,allow_blank =False)

	class Meta:
		model = UserUploadedFiles
		field = ('file',)
