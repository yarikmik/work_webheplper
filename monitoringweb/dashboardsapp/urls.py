from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from dashboardsapp.views import dashboard1

urlpatterns = [
    path('', dashboard1, name='dashboard1'),
]
