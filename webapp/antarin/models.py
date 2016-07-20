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

def get_upload_filepath(instance,filename):
    path_val=[]
    string_val = ""
    original_value = instance.folder
    if instance.folder is not None:
        while instance.folder.parentfolder is not None:
            path_val.append(instance.folder.name)
            instance.folder = instance.folder.parentfolder
        path_val.append(instance.folder.name)
        for i in range(len(path_val)-1,-1,-1):
            string_val = string_val + "/" + path_val[i]
        instance.folder = original_value
        argument_val = string_val[1:]
    else:
        argument_val = ''
    return 'userfiles/{0}/{1}/{2}'.format(instance.user.username,argument_val,filename)

class UserFolder(models.Model):
    user = models.ForeignKey(User,related_name='userfolders',null=True)
    name = models.CharField(max_length=60)
    parentfolder = models.ForeignKey('UserFolder',related_name='parentfoldername',null=True,on_delete=models.CASCADE)

class UserUploadedFiles(models.Model):
    user = models.ForeignKey(User,related_name='useruploadedfiles')
    file = models.FileField(upload_to =get_upload_filepath,blank=True,null=True)
    folder = models.ForeignKey(UserFolder,related_name='foldername',null=True,on_delete=models.CASCADE)
  
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)