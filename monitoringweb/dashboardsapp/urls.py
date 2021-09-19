from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from dashboardsapp.views import index

urlpatterns = [
    path('', index, name='index'),
]
