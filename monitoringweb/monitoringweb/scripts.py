from typing import Any
from django.conf import settings
from pyzabbix import ZabbixAPI
import os
import sys


def zabbix_connect():
    # Подключение к zabbixAPI
    z = ZabbixAPI(settings.ZABBIX_SERVER,
                  user=settings.ZABBIX_USER,
                  password=settings.ZABBIX_PASSWORD)
    # zapi.login(settings.ZABBIX_USER, settings.ZABBIX_PASSWORD)
    answer = z.do_request('apiinfo.version')
    print('Version:', answer['result'])
    return z


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
        limit=1,
    )
    filtering_trigger = []
    for trigger in triggers:
        #  дополнительный фильтр, проверяющий статус enable\disable у итема:
        if all([True if element['status'] == '0' else False for element in trigger['items']]):
            filtering_trigger.append(trigger)
    return filtering_trigger


def get_zabbix_trigger_in_problem():
    zapi = zabbix_connect()
    triggers = zapi.trigger.get(
        output=['triggerid', 'description',
                'comments', 'lastchange', 'priority'],
        selectLastEvent=['eventid', 'objectid',
                         'clock', 'value', 'acknowledged'],
        selectTriggers='extend',
        selectHosts=['name'],
        selectItems=['status'],
        active=True,
        withLastEventUnacknowledged=True,
        skipDependent=True,
        expandComment=True,
        expandDescription=True,
        expandExpression=True,
        filter={'value': 1, 'status': 0},
        sortfield='lastchange',
        sortorder='DESC',

    )
    filtering_trigger = []
    for trigger in triggers:
        #  дополнительный фильтр, проверяющий статус enable\disable у итема:
        if all([True if element['status'] == '0' else False for element in trigger['items']]):
            filtering_trigger.append(trigger)
    return filtering_trigger


def get_zabbix_problem():
    zapi = zabbix_connect()
    problems = zapi.problem.get(
        output='extend',
        source=0,
        object=0,
        selectHosts=['name'],
        selectAcknowledges=['extend'],
        # filter= {'suppressed': '1'},
        # sortfield='clock',
        # sortorder='DESC',
        # limit = 1,



    )
    return problems


def get_zabbix_events():

    # получение последних событий с триггера (или с любого объекта)
    zapi = zabbix_connect()
    events = zapi.event.get(
        output='extend',
        objectids='136533',  # ID триггера или объекта
        select_acknowledges='extend',
        selectTags='extend',
        selectSuppressionData='extend',
        sortfield=['clock', 'eventid'],
        sortorder='DESC',
    )
    return events


if __name__ == "__main__":
    sys.path.append("C:\PythonProjects\WebHelper\monitoringweb")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoringweb.settings")
    # zabbix_connect()
    print(get_zabbix_trigger_in_problem_test())
    # print(get_zabbix_events())
    # print(get_zabbix_problem())
