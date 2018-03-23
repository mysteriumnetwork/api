import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))  # noqa
import models
from models import db  # used for importing from other places
from queries import filter_active_sessions, filter_active_nodes
from datetime import datetime, timedelta
import humanize
import dashboard.helpers as helpers
from sqlalchemy import func, desc


def get_active_nodes_count():
    count = filter_active_nodes().count()
    return count


def get_active_sessions_count(node_key=None):
    query = filter_active_sessions()

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
            delta = se.node_updated_at - se.created_at
            total_seconds += delta.total_seconds()
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


def get_country_string(country):
    return country or 'N/A'


def get_nodes(limit=None):
    nodes = models.Node.query

    if limit:
        nodes = nodes.limit(limit)

    nodes = nodes.all()

    for node in nodes:
        node.country_string = get_country_string(
            node.get_country_from_service_proposal()
        )
        node.sessions_count = get_sessions_count(node_key=node.node_key)
        delta = datetime.utcnow() - node.updated_at
        node.last_seen = humanize.naturaltime(delta.total_seconds())
        node.status = get_node_status(node)

    return nodes


def get_available_nodes(limit=None):
    nodes = filter_active_nodes()

    if limit:
        nodes = nodes.limit(limit)

    nodes = nodes.all()

    for node in nodes:
        node.country_string = get_country_string(
            node.get_country_from_service_proposal()
        )
        node.sessions_count = get_sessions_count(node_key=node.node_key)
        node.uptime = 'N/A'
    return nodes


def get_node_status(node):
    return 'Online' if node.is_active() else 'Offline'


def get_node_info(node_key):
    def get_node_time_online(day):
        records_count = models.NodeAvailability.query.filter(
            models.NodeAvailability.node_key == node_key,
            day <= models.NodeAvailability.date,
            models.NodeAvailability.date < day+timedelta(days=1)
        ).count()

        if records_count > 24*60:
            # something broken
            pass

        return round(records_count / 60.0)

    node = models.Node.query.get(node_key)
    delta = datetime.utcnow() - node.updated_at
    node.last_seen = humanize.naturaltime(delta.total_seconds())
    node.country_string = get_country_string(
        node.get_country_from_service_proposal()
    )
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
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day = today - timedelta(days=i)
        availability.append({
            'day': day.strftime('%Y-%m-%d'),
            'time_online': get_node_time_online(day)
        })

    node.availability = availability

    day_before = datetime.utcnow() - timedelta(days=1)
    node.uptime = '{}h / 24h'.format(int(get_node_time_online(day_before)))
    node.status = get_node_status(node)

    return node


def enrich_session_info(se):
    duration = (se.node_updated_at or se.client_updated_at) - se.created_at
    duration_seconds = duration.total_seconds()
    m, s = divmod(duration_seconds, 60)
    h, m = divmod(m, 60)
    se.duration = "%d:%02d:%02d" % (h, m, s)
    se.data_sent = helpers.get_natural_size(se.client_bytes_sent)
    se.data_received = helpers.get_natural_size(se.client_bytes_received)
    se.data_transferred = helpers.get_natural_size(
        se.client_bytes_sent + se.client_bytes_received
    )
    session_time = datetime.utcnow() - se.created_at
    se.started = humanize.naturaltime(session_time.total_seconds())
    se.status = 'Ongoing' if se.is_active() else 'Completed'
    se.shortened_node_key = helpers.shorten_node_key(se.node_key)
    se.client_country_string = get_country_string(se.client_country)


def get_sessions(node_key=None, limit=None):
    if node_key:
        sessions = models.Session.query.filter(
            models.Session.node_key == node_key
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


def get_sessions_country_stats():
    results = db.session.query(
        models.Session.client_country,
        func.count(models.Session.session_key).label('count')
    ).group_by(models.Session.client_country).order_by(desc('count')).all()

    return results
