from django.shortcuts import render


def dashboard1(request):
    return render(request, 'dashboardsapp/dashboard1.html')
