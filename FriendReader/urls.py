"""FriendReader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from backend import views as backend_views
from django.conf.urls.static import static
from django.conf import settings
import frontend.views

urlpatterns = [
    url(r'^$',backend_views.testfuck),
    url(r'^users/$',backend_views.user,name = 'register'),
    url(r'^users/login/$',backend_views.login,name = 'login'),
    url(r'^users/logout/$',backend_views.logout,name = 'logout'),
    url(r'^friends/$',backend_views.myfriends,name = 'myfriends'),
    url(r'^friends/(\d+)/$',backend_views.friend,name = 'friend'),
    url(r'^friends/(\d+)/socials/(\d+)/$',backend_views.asocial,name = 'asocial'),


    url(r'^login/$', frontend.views.login),
    url(r'^register/$', frontend.views.register),
    url(r'^show/activities/', frontend.views.show_activities),
    url(r'^show/vitalities/$', frontend.views.show_vitalities),
    url(r'^show/interests/$', frontend.views.show_interests),
    url(r'^config/user/', frontend.views.config_user),
    url(r'^config/friends/$', frontend.views.config_friends),

    url(r'^activities/$',backend_views.activities,name = 'act'),
    url(r'^activities/(\d+)/$',backend_views.activity,name = 'act21'),
    url(r'^vitality/(\d+)/months/$',backend_views.vitalitymon,name = 'act23'),
    url(r'^vitality/(\d+)/days/$',backend_views.vitalityday,name = 'act4'),
    url(r'^interest/(\d+)/$',backend_views.interests,name = 'act5'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
