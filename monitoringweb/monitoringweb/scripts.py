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


def get_zabbix_trigger_in_problem():
    zapi = zabbix_connect()    
    triggers = zapi.trigger.get(
                output= ['triggerid', 'description', 'priority', 'time'],
                filter= {'value': 1},
                # withUnacknowledgedEvents = 'True',
                withLastEventUnacknowledged = 'True', 
                active = 'True',
                # selectTags = 'extend',
                sortfield = 'priority',
                # sortfield = 'clock',
                sortorder= 'DESC',
                #раскрытие макросов:
                expandComment = 'True',
                expandDescription = 'True',
                expandExpression = 'True',

    )
    return triggers

def get_zabbix_events():
    # получение последних событий с триггера (или с любого объекта)
    zapi = zabbix_connect()    
    events = zapi.event.get(
        output = 'extend', 
        objectids = '136533', # ID триггера или объекта
        select_acknowledges = 'extend',
        selectTags = 'extend',
        selectSuppressionData = 'extend',
        sortfield = ['clock', 'eventid'],
        sortorder = 'DESC',
    )
    return events

if __name__ == "__main__":
    sys.path.append("C:\PythonProjects\WebHelper\monitoringweb")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoringweb.settings")
    # zabbix_connect()
    # print(get_zabbix_trigger_in_problem())
    print(get_zabbix_events())
