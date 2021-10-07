from monitoringweb.scripts.zabbix_connection import zabbix_connect
import os
import sys


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
        min_severity=1,
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
