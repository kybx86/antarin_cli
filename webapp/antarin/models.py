#AUTHOR : RUCHIKA SHIVASWAMY
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

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

class AntarinFiles(models.Model):
    file = models.FileField(upload_to='antarin_files',blank=True,null=True)

class UserFolders(models.Model):
    user = models.ForeignKey(User,related_name='user_folders')
    foldername = models.CharField(max_length=60,null=True)
    parentfolder = models.ForeignKey('UserFolders',related_name='all_folders',null=True)

class UserFiles(models.Model):
    user = models.ForeignKey(User,related_name='user_files')
    file_ref = models.ForeignKey(AntarinFiles,related_name='file_ref')
    parentfolder = models.ForeignKey(UserFolders,related_name='all_files',null=True)

class AntarinSpaces(models.Model):
    name = models.CharField(max_length=120,unique=True)

class UserSpaces(models.Model):
    user = models.ForeignKey(User,related_name='user_spaces')
    space = models.ForeignKey(AntarinSpaces,related_name='all_user_spaces')
    STATUS_CHOICES = (
        ('A', 'Admin'),
        ('C', 'Contributor'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    access_key = models.IntegerField(default=0)

class AntarinSpaceFolders(models.Model):
    space = models.ForeignKey(AntarinSpaces,related_name='space_folders')
    foldername = models.CharField(max_length=60)
    parentfolder = models.ForeignKey('AntarinSpaceFolders',related_name='all_space_folders',null=True)
    added_by = models.ForeignKey(User,related_name='user_space_folders',null=True)

class AntarinSpaceFiles(models.Model):
    space = models.ForeignKey(AntarinSpaces,related_name='space_files')
    file_ref = models.ForeignKey(AntarinFiles,related_name='space_file_reference')
    parentfolder = models.ForeignKey(AntarinSpaceFolders,related_name='all_space_files',null=True)
    added_by = models.ForeignKey(User,related_name='user_space_files',null=True)

class AntarinSpaceLogs(models.Model):
    user = models.ForeignKey(User,related_name='user_space_log')
    space = models.ForeignKey(AntarinSpaces,related_name='space_reference')
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=600)

def get_keypath(instance,filename):
    foldername = keys
    return '{0}/{1}/{2}'.format(foldername,instance.region,filename)

class RSAKeys(models.Model):
    region = models.CharField(max_length=50)
    key_name = models.CharField(max_length=50)
    key = models.FileField(upload_to=get_keypath,blank=True,null=True)

class AntarinClouds(models.Model):
    user = models.ForeignKey(User,related_name='user_clouds')
    access_key = models.IntegerField(default=0)
    space = models.ForeignKey(AntarinSpaces,related_name='space_clouds')
    cloud_name = models.CharField(max_length=60,default='')
    instance_id = models.CharField(max_length=40,default='')
    ami_id = models.CharField(max_length=40)
    region = models.CharField(max_length=60,default='')
    #keyval = models.ForeignKey(RSAKeys,related_name='rsakeys',null=True,default='')
    instance_type = models.CharField(max_length=60)
    security_group = models.CharField(max_length=60,default='launch-wizard-2')
    dns_name = models.CharField(max_length=60,default='')
    is_active = models.BooleanField(default=False)
    package_active = models.CharField(max_length=100,default='')
    process_running = models.CharField(max_length=500,default='')
    status = models.CharField(max_length=200,default='Standby')

class AntarinCloudFolders(models.Model):
    cloud = models.ForeignKey(AntarinClouds,related_name='cloud_folders')
    foldername = models.CharField(max_length=60)
    parentfolder = models.ForeignKey('AntarinCloudFolders',related_name='all_cloud_folders',null=True)

class AntarinCloudFiles(models.Model):
    cloud = models.ForeignKey(AntarinClouds,related_name='cloud_files')
    file_ref = models.ForeignKey(AntarinFiles,related_name='cloud_file_reference')
    parentfolder = models.ForeignKey(AntarinCloudFolders,related_name='all_cloud_files',null=True)




# class AntarinFolders(models.Model):
#     user = models.ForeignKey(User,related_name='all_antarin_folders')
#     name = models.CharField(max_length=60)
#     parentfolder = models.ForeignKey('AntarinFolders',related_name='parent_folder_reference',null=True)

# class AntarinFiles(models.Model):
#     user = models.ForeignKey(User,related_name='all_antarin_files')
#     file = models.FileField(upload_to=get_upload_filepath,blank=True,null=True)
#     folder = models.ForeignKey(AntarinFolders,related_name='parent_folder_ref',null=True)

# class UserFiles(models.Model):
#     user = models.ForeignKey(User,related_name='user_files')
#     file_ref = models.ForeignKey(AntarinFiles,related_name='all_user_files')

# class UserFolders(models.Model):
#     user = models.ForeignKey(User,related_name='user_folders')
#     folder_ref = models.ForeignKey(AntarinFolders,related_name='all_user_folders',null=True)


# class AntarinProjectFiles(models.Model):
#     project = models.ForeignKey(AntarinProjects,related_name='project')
#     file_ref = models.ForeignKey(AntarinFiles,related_name='all_project_files')

# class AntarinProjectFolders(models.Model):
#     project = models.ForeignKey(AntarinProjects,related_name='project_ref')
#     folder_ref = models.ForeignKey(AntarinFolders,related_name='all_project_folders')

# class AntarinProjectLogs(models.Model):
#     user = models.ForeignKey(User,related_name='user_project_logs')
#     project = models.ForeignKey(AntarinProjects,related_name='project_reference')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     action = models.CharField(max_length=600)

# def get_keypath(instance,filename):
#     foldername = keys
#     return '{0}/{1}/{2}'.format(foldername,instance.region,filename)

# class RSAKeys(models.Model):
#     region = models.CharField(max_length=50)
#     key_name = models.CharField(max_length=50)
#     key = models.FileField(upload_to=get_keypath,blank=True,null=True)

# class AntarinProjectClouds(models.Model):
#     access_key = models.IntegerField(default=0)
#     project = models.ForeignKey(AntarinProjects,related_name='project_clouds')
#     cloud_name = models.CharField(max_length=60,default='')
#     instance_id = models.CharField(max_length=40,default='')
#     ami_id = models.CharField(max_length=40)
#     region = models.CharField(max_length=60,default='')
#     #keyval = models.ForeignKey(RSAKeys,related_name='rsakeys',null=True,default='')
#     instance_type = models.CharField(max_length=60)
#     security_group = models.CharField(max_length=60,default='launch-wizard-2')
#     dns_name = models.CharField(max_length=60,default='')
#     is_active = models.BooleanField(default=False)

# class UserClouds(models.Model):
#     user = models.ForeignKey(User,related_name='user_clouds')
#     cloud = models.ForeignKey(AntarinProjectClouds,related_name='all_user_clouds')

# class CloudFiles(models.Model):
#     cloud = models.ForeignKey(AntarinProjectClouds,related_name='cloud')
#     file_ref = models.ForeignKey(AntarinFiles,related_name='all_cloud_files')

# class CloudFolders(models.Model):
#     cloud = models.ForeignKey(AntarinProjectClouds,related_name='cloud_ref')
#     folder_ref = models.ForeignKey(AntarinFolders,related_name='all_cloud_folders')

#######################
# def get_upload_filepath(instance,filename):
#     path_val=[]
#     string_val = ""
#     original_value = instance.folder
#     if instance.folder is not None:
#         while instance.folder.parentfolder is not None:
#             path_val.append(instance.folder.name)
#             instance.folder = instance.folder.parentfolder
#         path_val.append(instance.folder.name)
#         for i in range(len(path_val)-1,-1,-1):
#             string_val = string_val + "/" + path_val[i]
#         instance.folder = original_value
#         argument_val = string_val[1:]
#     else:
#         argument_val = ''
#     return 'userfiles/{0}/{1}/{2}'.format(instance.user.username,argument_val,filename)

class UserFolder(models.Model):
    user = models.ForeignKey(User,related_name='userfolders',null=True)
    name = models.CharField(max_length=60)
    parentfolder = models.ForeignKey('UserFolder',related_name='parentfoldername',null=True,on_delete=models.CASCADE)

class UserUploadedFiles(models.Model):
    user = models.ForeignKey(User,related_name='useruploadedfiles')
    file = models.FileField(upload_to =get_upload_filepath,blank=True,null=True)
    folder = models.ForeignKey(UserFolder,related_name='foldername',null=True,on_delete=models.CASCADE)

# class Projects(models.Model):
#     name = models.CharField(max_length=120,unique=True)

# class UserProjects(models.Model):
#     user = models.ForeignKey(User,related_name = 'userprojects')
#     project = models.ForeignKey(Projects,related_name = 'projectdetails')
#     STATUS_CHOICES = (
#         ('A', 'Admin'),
#         ('C', 'Contributor'),
#     )
#     status = models.CharField(max_length=1, choices=STATUS_CHOICES)
#     access_key = models.IntegerField(default=0)

# class ProjectFolders(models.Model):
#     project = models.ForeignKey(Projects,related_name = 'projectfolders')
#     folder_ref = models.ForeignKey(UserFolder,related_name='projectfolderreference',null=True)

# class ProjectDetailsLogger(models.Model):
#     project = models.ForeignKey(Projects,related_name = 'projectlogs')
#     user = models.ForeignKey(User,related_name = 'user_projectlogs')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     action = models.CharField(max_length=600)

# class ProjectFiles(models.Model):
#     project = models.ForeignKey(Projects,related_name = 'projectfiles')
#     file_ref = models.ForeignKey(UserUploadedFiles,related_name = 'projectfilereference')
#     #file = models.FileField(upload_to=get_upload_projectfilepath,blank=True,null=True)
    
# def get_keypath(instance,filename):
#     foldername = keys
#     return '{0}/{1}/{2}'.format(foldername,instance.region,filename)

# class RSAKeys(models.Model):
#     region = models.CharField(max_length=50)
#     key_name = models.CharField(max_length=50)
#     key = models.FileField(upload_to=get_keypath,blank=True,null=True)

# class UserInstances(models.Model):
#     access_key = models.IntegerField(default=0)
#     user = models.ForeignKey(User,related_name='userinstances')
#     project = models.ForeignKey(Projects,related_name='projectinstances')
#     instance_name = models.CharField(max_length=60,default='')
#     instance_id = models.CharField(max_length=40,default='')
#     ami_id = models.CharField(max_length=40)
#     region = models.CharField(max_length=60,default='')
#     keyval = models.ForeignKey(RSAKeys,related_name='rsakeys',null=True,default='')
#     instance_type = models.CharField(max_length=60)
#     security_group = models.CharField(max_length=60,default='launch-wizard-2')
#     dns_name = models.CharField(max_length=60,default='')
#     is_active = models.BooleanField(default=False)
    
# class InstanceFolders(models.Model):
#     instance = models.ForeignKey(UserInstances,related_name='instancefolders')
#     project_folder_ref = models.ForeignKey(ProjectFolders,related_name='instance_folder_ref')

# class algoFiles(models.Model):
#     instance = models.ForeignKey(UserInstances,related_name='algofiles_instance_object')
#     projectfile = models.ForeignKey(ProjectFiles,related_name='algo_files')

# class dataFiles(models.Model):
#     instance = models.ForeignKey(UserInstances,related_name='datafiles_instance_object')
#     projectfile = models.ForeignKey(ProjectFiles,related_name='data_files')

###########################
# def get_upload_projectfilepath(instance,filename):
#     path_val=[]
#     string_val = ""
#     original_value = instance.projectfolder
#     if instance.projectfolder is not None:
#         while instance.projectfolder.parentfolder is not None:
#             path_val.append(instance.projectfolder.foldername)
#             instance.projectfolder = instance.projectfolder.parentfolder
#         path_val.append(instance.projectfolder.foldername)
#         for i in range(len(path_val)-1,-1,-1):
#             string_val = string_val + "/" + path_val[i]
#         instance.projectfolder = original_value
#         argument_val = string_val[1:]
#     else:
#         argument_val = ''
#     return 'projects/{0}/{1}/{2}'.format(instance.project.name,argument_val,filename)

