import models
import humanize
from datetime import timedelta, datetime
import calendar


def shorten_node_key(node_key):
    if node_key and len(node_key) == models.IDENTITY_LENGTH_LIMIT:
        return node_key[:6] + '..' + node_key[-4:]
    else:
        return node_key


def format_bytes_count(value):
    str_value = humanize.naturalsize(value, format='%.2f', binary=True)
    # KiB -> KB, MiB - > MB, ..
    return str_value.replace('i', '')


def format_duration(total_seconds: float) -> str:
    if total_seconds < 60:
        return '< 1 minute'
    total_minutes, _ = divmod(total_seconds, 60)
    hours, minutes = divmod(total_minutes, 60)
    result = ''
    if hours > 0:
        result += '%dhr ' % hours
    result += '%dmin' % minutes
    return result


# calculates week range starting from Monday to Monday from provided date
def get_week_range(date):
    monday = date + timedelta(days=-date.weekday(), weeks=0)
    monday_timestamp = calendar.timegm(monday.timetuple())
    date_from = datetime.utcfromtimestamp(monday_timestamp)
    date_to = date_from + timedelta(days=7)
    return date_from, date_to
