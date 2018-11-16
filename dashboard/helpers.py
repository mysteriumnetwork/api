import models
import humanize
from datetime import timedelta

def shorten_node_key(node_key):
    if node_key and len(node_key) == models.IDENTITY_LENGTH_LIMIT:
        return node_key[:6] + '..' + node_key[-4:]
    else:
        return node_key


def get_natural_size(value):
    str_value = humanize.naturalsize(value, format='%.2f', binary=True)
    # KiB -> KB, MiB - > MB, ..
    return str_value.replace('i', '')


def format_duration(duration: timedelta) -> str:
    result = ''
    total_seconds = duration.total_seconds()
    if total_seconds < 60:
        result = '< 1 minute'
    else:
        total_minutes, _ = divmod(total_seconds, 60)
        hours, minutes = divmod(total_minutes, 60)
        if hours > 0:
            result += '%dhr ' % hours
        result += '%dmin' % minutes
    return result
