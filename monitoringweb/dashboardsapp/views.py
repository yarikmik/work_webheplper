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

    duty_time = DutyTime()
    channels = ChannelsStatus(duty_time.start_duty(), duty_time.end_duty())
    context = {
        'title': title,
        'start_duty': duty_time.start_duty(),
        'end_duty': duty_time.end_duty(),
        'channels_down': channels.channels_in_problem(),
        'channels_up': channels.channels_was_in_problem(),
        'low_channels_down':channels.channels_low_priority_in_problem(),
        'low_channels_up':channels.channels_low_priority_was_in_problem(),
    }
    return render(request, 'dashboardsapp/Channels.html', context)
