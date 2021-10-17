from django import template
import datetime
register = template.Library()

def print_seconds_to_time(timestamp):
    try:
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.timedelta(seconds=ts)

register.filter(print_seconds_to_time)