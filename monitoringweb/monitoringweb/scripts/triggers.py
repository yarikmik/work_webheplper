from monitoringweb.scripts.zabbix_connection import zabbix_connect
import os
import sys


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
        min_severity = 1,
        active=True,
        maintenance=False,
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


if __name__ == "__main__":
    sys.path.append("C:\PythonProjects\WebHelper\monitoringweb")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoringweb.settings")
    print(get_zabbix_trigger_in_problem_test())
