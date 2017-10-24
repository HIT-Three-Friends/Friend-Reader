#- coding: utf-8
from django.db import models

class users(models.Model):
    username = models.CharField(primary_key = True, max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    friendnum = models.IntegerField(default=0)

class friends(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.CharField(max_length=20)
    friendid = models.IntegerField(default=0)
    name = models.CharField(max_length=20)
    sex = models.IntegerField(default=0)
    avatar = models.CharField(max_length=20)

class social(models.Model):
    id = models.IntegerField(primary_key=True)
    father = models.IntegerField(default=0)
    platform = models.IntegerField(default=0)
    account = models.CharField(max_length=20)

# Create your models here.