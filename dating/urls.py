""" Dating URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
"""

# dating/urls.py
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views
from django.conf.urls import handler404
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('landings.urls')),
    url(r'', include('manager.urls')),
    url(r'', include('dateSite.urls')),
    url(r'', include('allauth.urls')),
    # files upload
    url(r'^upload/', include('django_file_form.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
