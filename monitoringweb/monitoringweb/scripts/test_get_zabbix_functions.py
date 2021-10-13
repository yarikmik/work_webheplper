from zabbix_connection import zabbix_connect
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date, time, timedelta
import time


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



"""
Блок тестовых функций для составления отчета по недоступным каналам связи за определенный период
"""
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


def formatting_event_list(event_list, triggerid_pool):
    '''функия форматирует строку информации по событию в удобый формат'''
    new_event_list = {}
    for trigger in triggerid_pool:
        periods_list = []
        for event in event_list:
            # выводим в ключ id  триггера канала:
            if event['relatedObject']['triggerid'] == trigger:
                periods_list.append(
                    {'s_clock': event['clock'],  # в листе собираем список периодов недоступности
                    'r_clock': event['r_clock'], })
                new_event_list.update({trigger: {
                    # формируем новую структуру сводной информации по каналу
                    'name': event['name'],
                    'periods': periods_list,
                    'value': event['relatedObject']['value']}})
                # value=0 - в данный момент канал в работе, 1-проблема, триггер активен

    return new_event_list


def get_r_clock_from_event(t_from, t_till, zapi, event):
    '''функция для многопоточного запроса'''
    if event['r_eventid'] and event['r_eventid'] != '0':
        r_clock = zapi.event.get(eventids=event['r_eventid'])[0]['clock']
        if int(r_clock) >= t_from and int(r_clock) < t_till:
            event['r_clock'] = r_clock
            return event



def get_zabbix_events_in_period_test(t_from, t_till):
    """
    проблема возникшая в заданном периоде и в нем же восстановленная, + время восстановления
    """
    zapi = zabbix_connect()
    events = zapi.event.get(
        # objectids = ['59594'],
        output=['name', 'value', 'clock', 'r_eventid', 'severity'],
        source=0,  # только события от триггеров
        # severities = ['1','2','3','4','5'],
        selectRelatedObject=['triggerid', 'value'],
        search={'name': 'DOWN'},
        hostids=['12206'],
        time_from=t_from,
        time_till=t_till,
        filter={'value': 1},  # только события в состоянии "проблема"
        sortfield=['clock'],
        sortorder='DESC',
    )

    triggerid_pool = []
    for event in events:

        # составляем список уникалььных triggerid от которых генерируются ивенты:
        if event['relatedObject']['triggerid'] not in triggerid_pool:
            triggerid_pool.append(event['relatedObject']['triggerid'])

        # если времени восстоновления еще небыло, обозначаем его как null
        if event['r_eventid'] == '0':
            event['r_clock'] = 'null'
        else:
            # добавляем к словарю время восстановления события
            r_clock = zapi.event.get(eventids=event['r_eventid'])[0]['clock']
            event['r_clock'] = r_clock

    new_event_list = formatting_event_list(events, triggerid_pool)

    return new_event_list



def get_zabbix_events_restored_in_peeriod(t_from, t_till):
    """
    события восстановления, для случаев, когда проблема началась до выбранного периода, но восстановилась в нем
    """
    zapi = zabbix_connect()
    events = zapi.event.get(
        output=['name', 'value', 'clock', 'r_eventid', 'severity'],
        source=0,  # только события от триггеров
        selectRelatedObject=['triggerid', 'value'],
        search={'name': 'DOWN'},
        hostids=['12206'],
        r_eventid='extend',
        time_till=t_from,  # ищем события, которые были созданы до начала периода
        time_from=t_from - 5184000,  # ограничим 60 днями для сокращения выборки
        filter={'value': 1},  # только события в состоянии проблема
        sortfield=['clock'],
        sortorder='DESC',
    )

    events_end_problem_in_period = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        #  многопоточный запрос для поиска r_clock в заданном периоде
        future = [executor.submit(
            get_r_clock_from_event, t_from, t_till, zapi, event) for event in events]
        for event in as_completed(future):
            if event.result():
                events_end_problem_in_period.append(event.result())

    triggerid_pool = []
    for event in events_end_problem_in_period:
        # составляем список уникалььных triggerid от которых генерируются ивенты:
        if event['relatedObject']['triggerid'] not in triggerid_pool:
            triggerid_pool.append(event['relatedObject']['triggerid'])

    new_event_list = formatting_event_list(events_end_problem_in_period, triggerid_pool)

    return new_event_list


def get_zabbix_events_ongoing_in_peeriod(t_from, t_till):
    '''проблема началась до выбранного периода и еще активна '''
    pass


if __name__ == "__main__":
    from zabbix_connection import zabbix_connect
    # sys.path.append("C:\PythonProjects\WebHelper\monitoringweb")
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoringweb.settings")
    # print(get_zabbix_trigger_in_problem_test())
    # print(get_zabbix_problems_in_period_test())

    get_duty_period()
    # print(get_events_trigers())

    # print(get_zabbix_events_in_period_test(1633957200, 1634000400))
    print(get_zabbix_events_restored_in_peeriod(1633950800, 1633950900))
