from monitoringweb.scripts.zabbix_connection import zabbix_connect
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date, time, timedelta
from json import JSONEncoder

def formatting_event_list(event_list):
    '''функия форматирует строку информации по событию в удобый формат'''
    triggerid_pool = []
    for event in event_list:
        # составляем список уникалььных triggerid от которых генерируются ивенты:
        if event['relatedObject']['triggerid'] not in triggerid_pool:
            triggerid_pool.append(event['relatedObject']['triggerid'])

    new_event_list = {}
    for trigger in triggerid_pool:
        periods_list = []
        down_time = 0 #  переменная для подстчета общего времени недоступности
        for event in event_list:
            # выводим в ключ id  триггера канала:
            if event['relatedObject']['triggerid'] == trigger:
                r_clock = int(event['r_clock'] if event['r_clock'] != 'null' else datetime.today(
                ).replace(microsecond=0).timestamp())
                periods_list.append(
                    {'s_clock': event['clock'],  # в листе собираем список периодов недоступности
                     'r_clock': str(r_clock),
                     'event_time': r_clock-int(event['clock'])})
                down_time += r_clock-int(event['clock'])
                new_event_list.update({trigger: {
                    # формируем новую структуру сводной информации по каналу
                    'name': event['name'],
                    'periods': periods_list,
                    'down_time': down_time,
                    'value': event['relatedObject']['value'],
                    'priority': event['relatedObject']['priority']}})
                # value=0 - в данный момент канал в работе, 1-проблема, триггер активен

    #  теперь надо вывести получившиеся значения из под ключа id триггера
    return [event for event in new_event_list.values()]


def get_r_clock_from_event(t_from, t_till, zapi, event):
    '''функция для многопоточного запроса'''
    if event['r_eventid'] and event['r_eventid'] != '0':
        r_clock = zapi.event.get(eventids=event['r_eventid'])[0]['clock']
        if int(r_clock) >= t_from and int(r_clock) < t_till:
            event['r_clock'] = r_clock
            return event


def get_zabbix_events_in_period(t_from, t_till, zapi):
    """
    проблема возникшая в заданном периоде и в нем же восстановленная, + время восстановления
    """
    events = zapi.event.get(
        output=['name', 'value', 'clock', 'r_eventid'],
        source=0,  # только события от триггеров
        selectRelatedObject=['triggerid', 'value', 'priority'],
        search={'name': 'DOWN'},
        hostids=['12206'],
        time_from=t_from,
        time_till=t_till,
        filter={'value': 1},  # только события в состоянии "проблема"
        sortfield=['clock'],
        sortorder='DESC',
    )

    for event in events:

        # если времени восстоновления еще небыло, обозначаем его как null
        if event['r_eventid'] == '0':
            event['r_clock'] = 'null'
        else:
            # добавляем к словарю время восстановления события
            r_clock = zapi.event.get(eventids=event['r_eventid'])[0]['clock']
            event['r_clock'] = r_clock

    return events


def get_zabbix_events_restored_in_peeriod(t_from, t_till, zapi):
    """
    события восстановления, для случаев, когда проблема началась до выбранного периода, но восстановилась в нем
    """
    events = zapi.event.get(
        output=['name', 'value', 'clock', 'r_eventid'],
        source=0,  # только события от триггеров
        selectRelatedObject=['triggerid', 'value', 'priority'],
        search={'name': 'DOWN'},
        hostids=['12206'],
        time_till=int(t_from),  # ищем события, которые были созданы до начала периода
        time_from=int(t_from) - 5184000,  # ограничим 60 днями для сокращения выборки
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

    return events_end_problem_in_period


def get_zabbix_events_ongoing_in_peeriod(t_from, t_till, zapi):
    '''проблема началась до выбранного периода и еще активна '''
    triggers = zapi.trigger.get(
        output=['triggerid', 'description', 'lastchange'],
        selectLastEvent=['eventid'],
        search={'description': 'DOWN'},
        hostids=['12206'],
        # возврат только тех триггеров, которые изменили свое состояние до начала периода
        lastChangeTill=t_from,
        filter={'value': 1, 'status': 0},
        sortfield='lastchange',
        sortorder='DESC',
    )

    events = zapi.event.get(
        eventids=[trigger['lastEvent']['eventid'] for trigger in triggers],
        output=['name', 'value', 'clock', 'r_eventid'],
        source=0,  # только события от триггеров
        selectRelatedObject=['triggerid', 'value', 'priority'],
        search={'name': 'DOWN'},
        hostids=['12206'],
        filter={'value': 1},  # только события в состоянии проблема
        sortfield=['clock'],
        sortorder='DESC',
    )

    for event in events:

        # если времени восстоновления еще небыло, обозначаем его как null
        if event['r_eventid'] == '0':
            event['r_clock'] = 'null'
        else:
            # добавляем к словарю время восстановления события
            r_clock = zapi.event.get(eventids=event['r_eventid'])[0]['clock']
            event['r_clock'] = r_clock

    # new_event_list = formatting_event_list(events, triggerid_pool)
    return events


def summarize_channels_problems(t_from, t_till):
    zapi = zabbix_connect()
    fool_event_pool = get_zabbix_events_in_period(t_from, t_till, zapi) + get_zabbix_events_restored_in_peeriod(
        t_from, t_till, zapi) + get_zabbix_events_ongoing_in_peeriod(t_from, t_till, zapi)
    return formatting_event_list(fool_event_pool)


class ChannelsStatus:

    def __init__(self, t_from, t_till):
        self.t_from = t_from
        self.t_till = t_till
        self.fool_event_pool = summarize_channels_problems(
            int(self.t_from), int(self.t_till))

    def channels_in_problem(self):
        return [event for event in self.fool_event_pool if event['value'] == '1' and event['priority'] != '0']

    def channels_was_in_problem(self):
        return [event for event in self.fool_event_pool if event['value'] == '0' and event['priority'] != '0']

    def channels_low_priority_in_problem(self):
        return [event for event in self.fool_event_pool if event['value'] == '1' and event['priority'] == '0']
    def channels_low_priority_was_in_problem(self):
        return [event for event in self.fool_event_pool if event['value'] == '0' and event['priority'] == '0']


if __name__ == "__main__":
    from zabbix_connection import zabbix_connect
    duty_time = ChannelsStatus(1634259600, 1634302800)
    print('каналы в статусе проблема:')
    print(duty_time.channels_in_problem())
    print('-*-*-*-*-*-')
    print('каналы были в статусе проблема:')
    print(duty_time.channels_was_in_problem())
    print('-*-*-*-*-*-')
    print('каналы с низким приоритетом в проблема:')
    print(duty_time.channels_low_priority_in_problem())
    print('-*-*-*-*-*-')
    print('каналы с низким приоритетом были в проблеме:')
    print(duty_time.channels_low_priority_was_in_problem())
    print('-*-*-*-*-*-')
