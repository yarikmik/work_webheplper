from django import template
import datetime
register = template.Library()

def print_convert_seconds(timestamp):
    try:
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.timedelta(seconds=ts)

register.filter(print_convert_seconds)