from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile')
    activation_key = models.CharField(max_length=60)
    key_expires = models.DateTimeField()