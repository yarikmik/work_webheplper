from django.shortcuts import render
from monitoringweb.scripts.triggers import get_zabbix_trigger_in_problem
from monitoringweb.scripts.channels import ChannelsStatus
from dashboardsapp.models import DutyTime


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


def channels(request):
    title = 'Каналы'
    duty_time = ChannelsStatus(DutyTime.start_duty(), DutyTime.end_duty())
    context = {
        'title': title,
        'start_duty': DutyTime.start_duty,
        'end_duty': DutyTime.end_duty,
        'channels_down': duty_time.channels_in_problem(),
        'channels_up': duty_time.channels_was_in_problem(),
    }
    return render(request, 'dashboardsapp/Channels.html', context)
