# Скрипт добавляет хосты в заббикс из списска в текстовом файле
from logging import exception
from zabbix_connection import zabbix_connect
import re
import os
import sys
import json

'''
Interface type.

Possible values are:
1 - agent;
2 - SNMP;
3 - IPMI;
4 - JMX.
'''

# regex = re.compile('(?P<host>\S+)(\s*|\t)(?P<ip>\S+$)')
regex = re.compile('(?P<host>^.+\s)(\s*|\t)(?P<ip>\d+.\d+.\d+.\d+)')

# templateZabbixName = "Template OGK Infrastructure ICMP Ping"
templateId = "11603"
# groupZabbixName = "OGK Tetra infrastructure"
groupid = "269"

result = {}

with open(os.path.join(sys.path[0], 'host_list.txt'), 'r') as file:
    for s in file:
        match = regex.search(s)
        if match:
            result.update({match.group("host"): match.group("ip")})  # Словарь устройство:адрес
print(result)


def addHost():
    # Функция перебирает словарь из имен и адресов и создает хосты в zabbix
    z = zabbix_connect()
    count = 0
    for h in result:
        hostname = h.strip()
        ip = result[h]

        try:
            z.host.create(
                host = hostname,
                interfaces =[{
                        "type": 2,
                        "main": 1,
                        "useip": 1,
                        "ip": ip,
                        "dns": "",
                        "port": "161",
                        "details": {
                            "version": 2,
                            "community": "{$SNMP_COMMUNITY}",
                        },
                    }],
                groups = [{
                        "groupid": groupid,
                    }],
                templates = [{
                        "templateid": templateId,
                    }],
                macros = [{
                        "macro": "{$SNMP_COMMUNITY}",
                        "value": "",
                    },
                    # {
                    #     "macro": "{$FILTER_LLD_PORTS}",
                    #     "value": "none"
                    # }
                ],
                tags =  [
                {
                    "tag": "location",
                    "value": "OGK test"
                }]
            )
            print(f'Хост:{hostname} был добавлен')
            count += 1
        except Exception as err:
            data = err.__dict__['error']['data']
            print(f'Хост:{hostname} Не добавлен!!! error: {data}')
    print("Добавлено " + str(count) + " хостов")

if __name__ == "__main__":
    addHost()
