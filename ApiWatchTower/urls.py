"""
ApiWatchTower URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Uncomment next two lines to enable admin:
from django.contrib import admin
from django.urls import path, re_path
from django.urls import *
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
  
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.conf.urls import include, url
from django.contrib import admin
import azure_ad_auth

from django.views.static import serve

# admin.autodiscover()

urlpatterns = [
    # Uncomment the next line to enable the admin:
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url="/admin/"), name='go-to-admin'),
    path('azure/', include('azure_ad_auth.urls')),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from azure_ad_auth.views import auth, complete
from django.conf.urls import url

urlpatterns += [
    url(r'^login/$', auth, name='azure_login'),
    url(r'^complete/$', complete, name='azure_complete'),
]