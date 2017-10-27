#- coding: utf-8
from django.db import models

class users(models.Model):
    username = models.CharField(primary_key = True, max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    friendnum = models.IntegerField(default=0)

    def __int__(self):
        return self.friendnum

class friends(models.Model):
    user = models.CharField(max_length=20)
    friendid = models.IntegerField(default=0)
    name = models.CharField(max_length=20)
    sex = models.IntegerField(default=0)
    avatar = models.ImageField(null=True,blank=True,upload_to="upload")

class social(models.Model):
    father = models.IntegerField(default=0)
    platform = models.IntegerField(default=0)
    account = models.CharField(max_length=20)

# Create your models here.