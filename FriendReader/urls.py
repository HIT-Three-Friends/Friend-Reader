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
import  time

urlpatterns = [
    url(r'^$',backend_views.testfuck),
    url(r'^users/$',backend_views.user,name = 'register'),
    url(r'^users/login/$',backend_views.login,name = 'login'),
    url(r'^users/logout/$',backend_views.logout,name = 'logout'),
    url(r'^friends/$',backend_views.myfriends,name = 'myfriends'),
    url(r'^friends/(\d+)/$',backend_views.friend,name = 'friend'),
    url(r'^friends/(\d+)/socials/(\d+)/$',backend_views.asocial,name = 'asocial'),

    url(r'^attentions/$',backend_views.myfocus,name = 'myfocus'),
    url(r'^attentions/(\d+)/$',backend_views.focu,name = 'focu'),

    url(r'^login/$', frontend.views.login),
    url(r'^register/$', frontend.views.register),
    url(r'^show/activities/', frontend.views.show_activities),
    url(r'^show/vitalities/$', frontend.views.show_vitalities),
    url(r'^show/interests/$', frontend.views.show_interests),
    url(r'^config/user/', frontend.views.config_user),
    url(r'^config/friends/$', frontend.views.config_friends),
    url(r'^show/changes/$', frontend.views.show_changes),
    url(r'^show/interactions$', frontend.views.show_interactions),
    url(r'^test/callback$', frontend.views.test_callback),

    url(r'^activities/$', backend_views.activitiesplatform, name='actp'),
    url(r'^activities/(\d+)/$', backend_views.activityplatform, name='act21p'),

    url(r'^vitality/(\d+)/months/$',backend_views.vitalitymon,name = 'act23'),
    url(r'^vitality/(\d+)/days/$',backend_views.vitalityday,name = 'act4'),
    url(r'^interest/(\d+)/$',backend_views.interests,name = 'act5'),
    url(r'^interest/(\d+)/months/$',backend_views.interestmonth,name = 'act6'),
    url(r'^interest/(\d+)/years/$',backend_views.interestyear,name = 'act7'),
    url(r'^interaction/(\d+)/$',backend_views.interaction,name = 'act8'),

    url(r'^token/$',backend_views.gettoken,name = 'act9'),
    url(r'^code/$',backend_views.putcode,name = 'act18'),
    url(r'^comment/(\d+)/$',backend_views.comment,name = 'act28'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
from apscheduler.scheduler import Scheduler
sched = Scheduler()
@sched.interval_schedule(seconds=600)
def mytask():
    print("cnm600")
    backend_views.refresh()
sched.start()