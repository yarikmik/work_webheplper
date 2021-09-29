from django.conf import settings
from pyzabbix import ZabbixAPI
import sys
import os

def zabbix_connect():
    # Подключение к zabbixAPI
    sys.path.append("C:\PythonProjects\WebHelper\monitoringweb")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoringweb.settings")

    z = ZabbixAPI(settings.ZABBIX_SERVER,
                  user=settings.ZABBIX_USER,
                  password=settings.ZABBIX_PASSWORD)
    # zapi.login(settings.ZABBIX_USER, settings.ZABBIX_PASSWORD)
    answer = z.do_request('apiinfo.version')
    
    print('Version:', answer['result'])
    return z


