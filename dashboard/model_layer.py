import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import models
from models import db  # used for importing from other places
from datetime import datetime, timedelta
import humanize
from geoip import geolite2

NODE_AVAILABILITY_TIMEOUT = 2

def get_active_nodes_count():
    count = models.Node.query.filter(
        models.Node.updated_at >= datetime.utcnow() - timedelta(minutes=NODE_AVAILABILITY_TIMEOUT)
    ).count()
    return count


def get_active_sessions_count(node_key=None):
    query = models.Session.query.filter(
        models.Session.client_updated_at >= datetime.utcnow() - timedelta(minutes=NODE_AVAILABILITY_TIMEOUT),
    )

    if node_key:
        query = query.filter(models.Session.node_key == node_key)

    count = query.count()
    return count


def get_sessions_count(node_key=None):
    if node_key:
        query = models.Session.query.filter(
            models.Session.node_key == node_key
        )
    else:
        query = models.Session.query
    return query.count()


def get_average_session_time():
    sessions = models.Session.query.all()

    count = 0
    total_seconds = 0

    for se in sessions:
        if se.node_updated_at:
            total_seconds += (se.node_updated_at - se.created_at).total_seconds()
            count += 1

    average_seconds = total_seconds / count if count != 0 else 0

    minutes = (average_seconds % 3600) // 60
    return '{0:.0f}'.format(minutes)


def get_total_data_transferred():
    sessions = models.Session.query.all()

    total_bytes = 0
    for se in sessions:
        total_bytes += se.client_bytes_sent
        total_bytes += se.client_bytes_received
    return '{0:.1f}'.format(total_bytes / 1024.0 / 1024.0)


def get_country_from_ip(ip):
    match = geolite2.lookup(ip)
    if match:
        return match.country

    return 'N/A'


def get_nodes(limit=None):
    nodes = models.Node.query

    if limit:
        nodes = nodes.limit(limit)

    nodes = nodes.all()

    for node in nodes:
        node.country = get_country_from_ip(node.ip)
        node.sessions_count = get_sessions_count(node_key=node.node_key)
        node.last_seen = humanize.naturaltime((datetime.utcnow() - node.updated_at).total_seconds())
        node.status = get_node_status(node)

    return nodes


def get_available_nodes(limit=None):
    nodes = models.Node.query.filter(
        models.Node.updated_at >= datetime.utcnow() - timedelta(minutes=NODE_AVAILABILITY_TIMEOUT)
    )

    if limit:
        nodes = nodes.limit(limit)

    nodes = nodes.all()

    for node in nodes:
        node.country = get_country_from_ip(node.ip)
        node.sessions_count = get_sessions_count(node_key=node.node_key)
        node.uptime = 'N/A'
    return nodes


def get_node_status(node):
    return 'Online' if datetime.utcnow() - node.updated_at <= timedelta(minutes=NODE_AVAILABILITY_TIMEOUT) else 'Offline'


def get_node_info(node_key):
    def get_node_time_online(day):
        records_count = models.NodeAvailability.query.filter(
            models.NodeAvailability.node_key==node_key,
            day <= models.NodeAvailability.date,
            models.NodeAvailability.date < day+timedelta(days=1)
        ).count()

        if records_count > 24*60:
            # something broken
            pass

        return round(records_count / 60.0)

    node = models.Node.query.get(node_key)
    node.last_seen = humanize.naturaltime((datetime.utcnow() - node.updated_at).total_seconds())
    node.country = get_country_from_ip(node.ip)
    node.sessions = get_sessions(node_key=node_key)

    total_bytes = 0
    for se in node.sessions:
        total_bytes += se.client_bytes_sent
        total_bytes += se.client_bytes_received

    node.data_transferred = '{0:.1f}'.format(total_bytes)
    node.sessions_count = get_sessions_count(node_key)

    availability = []

    # 7 days
    for i in range(6, -1, -1):
        day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        availability.append( {'day': day.strftime('%Y-%m-%d'), 'time_online': get_node_time_online(day)} )

    node.availability = availability

    node.uptime = '{}h / 24h'.format(int(get_node_time_online(datetime.utcnow() - timedelta(days=1))))
    node.status = get_node_status(node)

    return node


def enrich_session_info(se):
    duration_seconds = ((se.node_updated_at or se.client_updated_at) - se.created_at).total_seconds()
    m, s = divmod(duration_seconds, 60)
    h, m = divmod(m, 60)
    se.duration = "%d:%02d:%02d" % (h, m, s)
    se.client_bytes_sent = se.client_bytes_sent / 1024
    se.client_bytes_received = se.client_bytes_received / 1024
    se.data_transferred = se.client_bytes_sent + se.client_bytes_received
    se.started = humanize.naturaltime((datetime.utcnow() - se.created_at).total_seconds())
    se.status = 'Ongoing' if ((se.node_updated_at or se.client_updated_at) >= datetime.utcnow() - timedelta(minutes=NODE_AVAILABILITY_TIMEOUT)) else 'Completed'


def get_sessions(node_key=None, limit=None):
    if node_key:
        sessions = models.Session.query.filter(
            models.Session.node_key==node_key
        )
    else:
        sessions = models.Session.query

    sessions = sessions.order_by(models.Session.created_at.desc())

    if limit:
        sessions = sessions.limit(limit)

    sessions = sessions.all()

    for se in sessions:
        enrich_session_info(se)

    return sessions


def get_session_info(session_key):
    se = models.Session.query.get(session_key)
    enrich_session_info(se)
    return se
