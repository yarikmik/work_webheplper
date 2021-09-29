from django.shortcuts import render
from monitoringweb.scripts.triggers import get_zabbix_trigger_in_problem


def dashboard1(request):
    title = 'Дашборд 1'

    context = {
        'title': title,
        'alerts': get_zabbix_trigger_in_problem()
    }

    return render(request, 'dashboardsapp/dashboard1.html', context)


def dashboard2(request):
    title = 'Дашборд 2'

    context = {
        'title': title,
    }
    return render(request, 'dashboardsapp/dashboard1_copy.html', context)


