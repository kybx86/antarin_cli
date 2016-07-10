#AUTHOR : RUCHIKA SHIVASWAMY
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings

'''
A userprofile model with fields activation_key,key_expires and password_reset_key is linked to the User model, with user being the foreign key.
'''
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile')
    activation_key = models.CharField(max_length=60)
    key_expires = models.DateTimeField()
    password_reset_key = models.CharField(max_length=60)
    total_data_storage = models.CharField(max_length=20,default="5 GB")
    data_storage_used = models.CharField(max_length=20,default="0 GB")

class UserUploadedFiles(models.Model):
	user = models.ForeignKey(User,related_name='useruploadedfiles')
	file = models.FileField(upload_to ='user_files',blank=True,null=True)
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)