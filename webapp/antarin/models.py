from django.db import models
from django.contrib.auth.models import User

'''
A userprofile model with fields activation_key,key_expires and password_reset_key is linked to the User model, with user being the foreign key.
'''
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile')
    activation_key = models.CharField(max_length=60)
    key_expires = models.DateTimeField()
    password_reset_key = models.CharField(max_length=60)