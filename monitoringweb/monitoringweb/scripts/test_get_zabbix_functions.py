from zabbix_connection import zabbix_connect
import os
import sys
from datetime import datetime, date, time, timedelta
import time


def get_zabbix_trigger_in_problem_test():
    zapi = zabbix_connect()
    triggers = zapi.trigger.get(
        # output = ['triggerid', 'description', 'comments', 'lastchange', 'priority'],
        output='extend',
        # selectLastEvent = ['eventid', 'suppressed', 'clock', 'value', 'acknowledged'],
        selectLastEvent='extend',
        selectTriggers='extend',
        # selectGroups= ['name'],
        # selectHosts = ['name'],
        selectItems=['status'],
        # active = 1,
        withLastEventUnacknowledged=1,
        skipDependent=1,
        expandComment=1,
        expandDescription=1,
        expandExpression=1,
        filter={'value': 1, 'status': 0},
        sortfield='lastchange',
        sortorder='DESC',
        limit=10,
    )
    filtering_trigger = []
    for trigger in triggers:
        #  дополнительный фильтр, проверяющий статус enable\disable у итема:
        if all([True if element['status'] == '0' else False for element in trigger['items']]):
            filtering_trigger.append(trigger)
    return filtering_trigger


def get_zabbix_channels_in_period_test(t_from, t_till):
    zapi = zabbix_connect()
    channels = zapi.event.get(
        # objectids = ['59594'],
        output=['name','value', 'clock', 'r_eventid', 'severity'],
        source=0,  # только события от триггеров
        # severities = ['1','2','3','4','5'],
        search={'name': 'DOWN'},
        hostids=['12206'],
        time_from=t_from,
        time_till=t_till,
        # filter={'value': 1},
        sortfield=['clock'],
        sortorder='DESC',
    )
    for channel in channels:
        if channel['r_eventid'] == '0':
            channel['r_clock'] = 'null'
        else:
            # добавляем к словарю время восстановления события
            r_clock = zapi.event.get(eventids=channel['r_eventid'])[0]['clock']
            channel['r_clock'] = r_clock
    return channels


def get_duty_period():
    now = datetime.today()
    now = now.replace(microsecond=0)
    print(now)
    print(now.hour)
    if now.hour < 8 or now.hour < 20:
        start_duty = now - timedelta(days=1, hours=now.hour,
                                     minutes=now.minute, seconds=now.second) + timedelta(hours=20)
        end_duty = now - timedelta(hours=now.hour,
                                   minutes=now.minute, seconds=now.second) + timedelta(hours=8)
    else:
        start_duty = now - timedelta(hours=now.hour,
                                     minutes=now.minute, seconds=now.second) + timedelta(hours=8)
        end_duty = now - timedelta(hours=now.hour,
                                   minutes=now.minute, seconds=now.second) + timedelta(hours=20)

    start_duty_ts = int(start_duty.timestamp())
    end_duty_ts = int(end_duty.timestamp())

    print('начало смены: ' + start_duty.strftime('%Y-%m-%d %H:%M:%S') +
          ' timestamp=' + str(start_duty_ts))
    print('конец смены: ' + end_duty.strftime('%Y-%m-%d %H:%M:%S') +
          ' timestamp=' + str(end_duty_ts))


if __name__ == "__main__":
    from zabbix_connection import zabbix_connect
    # sys.path.append("C:\PythonProjects\WebHelper\monitoringweb")
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoringweb.settings")
    # print(get_zabbix_trigger_in_problem_test())
    # print(get_zabbix_problems_in_period_test())

    get_duty_period()
    # print(get_channels_trigers())
    print(get_zabbix_channels_in_period_test(1633957200,1634000400))
