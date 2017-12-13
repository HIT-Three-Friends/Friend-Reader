#- coding: utf-8
from django.db import models
import django.utils.timezone as timezone
class users(models.Model):
    username = models.CharField(primary_key = True, max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=40)
    friendnum = models.IntegerField(default=0)
    token = models.CharField(max_length=300)
    def __int__(self):
        return self.friendnum

class friends(models.Model):
    user = models.CharField(max_length = 20)
    friendid = models.IntegerField(default = 0)
    name = models.CharField(max_length = 30)
    sex = models.IntegerField(default = 0)
    avatar = models.ImageField(null = True,blank = True,upload_to = "upload")
    #zhihuid = friendid = models.IntegerField(default=0)
    #weiboid = friendid = models.IntegerField(default=0)
    #githubid = friendid = models.IntegerField(default=0)

class social(models.Model):
    father = models.IntegerField(default = 0)
    platform = models.IntegerField(default = 0)
    account = models.CharField(max_length = 30)
    time = models.DateTimeField(default = timezone.now)

class allactivity(models.Model):
    father = models.IntegerField(default = 0)
    username = models.CharField(max_length = 30)
    avatar_url = models.CharField(max_length = 300)
    headline = models.TextField()
    time = models.DateTimeField(default = timezone.now)
    actionType = models.TextField()
    summary = models.TextField()
    targetText = models.TextField()
    source_url = models.CharField(max_length = 300)
    mid = models.IntegerField(default=-1)

class focus(models.Model):
    father = models.CharField(max_length = 300)
    tag = models.CharField(max_length = 300,default='软件工程')

class pics(models.Model):
    father = models.IntegerField(default=0)
    imgs = models.CharField(max_length = 300)

class topic(models.Model):
    father = models.IntegerField(default=0)
    topics = models.CharField(max_length = 300)

class Picture(models.Model):
    """docstring for Picture"""
    user = models.IntegerField(default=0)
    image = models.ImageField(null=True, blank=True, upload_to="upload")

class friendfriend(models.Model):
    father = models.IntegerField(default=0)
    account = models.CharField(max_length=300)
    loved = models.FloatField(default=0.0)
    love = models.FloatField(default=0.0)

class friendtopic(models.Model):
    father = models.IntegerField(default = 0)
    topics = models.CharField(max_length=300)
    pp = models.FloatField(default=0.0)

# Create your models here.