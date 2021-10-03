from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from dashboardsapp.views import dashboard1, dashboard2


app_name = 'dashboardsapp'

urlpatterns = [
    path('', dashboard1, name='dashboard1'),
    path('dashboard2/', dashboard2, name='dashboard2'),
    ]
