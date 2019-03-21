import models
from queries import filter_active_sessions, filter_active_nodes
from queries import get_active_nodes_count_query
from datetime import datetime, timedelta
import humanize
import dashboard.helpers as helpers
from sqlalchemy import func, desc, text


def get_db():
    return models.db


def get_active_nodes_count():
    count = get_active_nodes_count_query().first()
    if len(count) == 1:
        return count[0]
    return 0


def get_sessions_count(node_key=None, only_active_sessions=False):
    if only_active_sessions:
        query = filter_active_sessions()
    else:
        query = models.Session.query

    if node_key:
        query = query.filter(models.Session.node_key == node_key)

    return query.count()


def get_sessions_count_by_service_type(node_key, service_type):
    query = models.Session.query.with_entities(func.count()).filter(
        models.Session.node_key == node_key,
        models.Session.service_type == service_type
    )
    return query.scalar()


def get_average_session_time():
    sql = text("""select
    AVG(TIME_TO_SEC(TIMEDIFF(client_updated_at, created_at)))
    as averageDuration FROM session;""")
    result = models.db.engine.execute(sql)
    myrow = result.fetchone()
    seconds = int(myrow[0])
    return helpers.format_duration(timedelta(seconds=seconds))


def get_total_data_transferred():
    sql = text("""select SUM(client_bytes_sent) as clientBytesSent,
    SUM(client_bytes_received) as clientBytesReceived FROM session;""")
    result = models.db.engine.execute(sql)
    myrow = result.fetchone()
    total_bytes = myrow[0] + myrow[1]
    return helpers.get_natural_size(total_bytes)


def aggregate_node_data_from_sessions(node_key, service_type, date_from, date_to):
    query = models.Session.query.with_entities(
        func.sum(models.Session.client_bytes_sent)
            .label('total_bytes_sent'),
        func.sum(models.Session.client_bytes_received)
            .label('total_bytes_received'),
        func.count()
            .label('total_sessions'),
     ).filter(
        models.Session.node_key == node_key,
        models.Session.service_type == service_type,
        date_from <= models.Session.client_updated_at,
        models.Session.client_updated_at < date_to,
    )
    row = query.one()
    bytes_sent = int(row[0] or 0)
    bytes_received = int(row[1] or 0)
    sessions_count = int(row[2] or 0)
    bytes_total = bytes_sent + bytes_received
    return sessions_count, bytes_total


def get_country_string(country):
    return country or 'N/A'


def get_nodes(limit=None):
    nodes = models.Node.query.order_by(models.Node.updated_at.desc())

    if limit:
        nodes = nodes.limit(limit)

    nodes = nodes.all()

    for node in nodes:
        node.country_string = get_country_string(
            node.get_country_from_service_proposal()
        )
        node.sessions_count = get_sessions_count_by_service_type(
            node.node_key, node.service_type
        )
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
        node.sessions_count = get_sessions_count_by_service_type(
            node.node_key, node.service_type
        )
        delta = datetime.utcnow() - node.updated_at
        node.last_seen = humanize.naturaltime(delta.total_seconds())
    return nodes


def get_node_hours_online(node_key, service_type, date_from, date_to) -> int:
    query = models.NodeAvailability.query.with_entities(func.count()).filter(
        models.NodeAvailability.node_key == node_key,
        models.NodeAvailability.service_type == service_type,
        date_from <= models.NodeAvailability.date,
        models.NodeAvailability.date < date_to
    )
    records_count = query.scalar()
    return int(round(records_count / 60.0))


def get_registered_nodes(date_from, date_to):
    query = models.Node.query.join(
        models.IdentityRegistration,
        models.IdentityRegistration.identity == models.Node.node_key,
    ).filter(
        date_from <= models.Node.updated_at,
        models.Node.updated_at < date_to
    )
    return query.all()


def enrich_registered_nodes_info(nodes, date_from, date_to):
    for node in nodes:
        node.country_string = get_country_string(
            node.get_country_from_service_proposal()
        )
        sessions_count, total_bytes = aggregate_node_data_from_sessions(
            node.node_key, node.service_type, date_from, date_to
        )
        node.sessions_count = sessions_count
        node.data_transferred = helpers.get_natural_size(total_bytes)
        hours_online = get_node_hours_online(
            node.node_key,
            node.service_type,
            date_from, date_to
        )
        node.availability = '{} / 168 h'.format(hours_online)


def get_node_status(node):
    return 'Online' if node.is_active() else 'Offline'


def get_node_info(node_key, service_type):
    node = models.Node.query.get([node_key, service_type])
    delta = datetime.utcnow() - node.updated_at
    node.last_seen = humanize.naturaltime(delta.total_seconds())
    node.country_string = get_country_string(
        node.get_country_from_service_proposal()
    )
    node.sessions = get_sessions(
        node_key=node_key,
        service_type=service_type,
        limit=10
    )

    total_bytes = 0
    for se in node.sessions:
        total_bytes += se.client_bytes_sent
        total_bytes += se.client_bytes_received

    node.data_transferred = helpers.get_natural_size(total_bytes)
    node.sessions_count = get_sessions_count_by_service_type(
        node_key,
        service_type
    )

    availability = []

    # 7 days
    for i in range(6, -1, -1):
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day = today - timedelta(days=i)
        availability.append({
            'day': day.strftime('%Y-%m-%d'),
            'time_online': get_node_hours_online(
                node_key,
                service_type,
                day,
                day + timedelta(days=1)
            )
        })

    node.availability = availability
    node.uptime = '{} / 24 h'.format(get_node_hours_online(
        node_key,
        service_type,
        datetime.utcnow() - timedelta(days=1),
        datetime.utcnow()
    ))
    node.status = get_node_status(node)
    return node


def enrich_session_info(se):
    duration = (se.node_updated_at or se.client_updated_at) - se.created_at
    se.duration = helpers.format_duration(duration)
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


def get_sessions(node_key=None, service_type=None, limit=None):
    if node_key and service_type:
        sessions = models.Session.query.filter(
            models.Session.node_key == node_key,
            models.Session.service_type == service_type
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
    if se is not None:
        enrich_session_info(se)
    return se


def get_sessions_country_stats():
    results = get_db().session.query(
        models.Session.client_country,
        func.count(models.Session.session_key).label('count')
    ).group_by(models.Session.client_country).order_by(desc('count')).all()

    return results
