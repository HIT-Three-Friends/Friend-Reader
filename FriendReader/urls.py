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
    url(r'^friend/(\d+)/$',backend_views.friend,name = 'friend'),
    url(r'^socials/(\d+)/$',backend_views.socials,name = 'socials'),
    url(r'^social/(\d+)/(\d+)/$',backend_views.asocial,name = 'asocial'),

    url(r'^login/', frontend.views.login),
    url(r'^register/', frontend.views.register),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
