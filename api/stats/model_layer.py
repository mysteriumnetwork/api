from queries import (
    filter_active_sessions,
    filter_active_nodes,
    get_active_nodes_count_query
)
from api.stats.db_queries.node_availability import get_node_hours_online
from datetime import datetime, timedelta
from sqlalchemy import func, desc, text
from models import db, Node, Session


def get_active_nodes_count():
    count = get_active_nodes_count_query().first()
    if len(count) == 1:
        return count[0]
    return 0


def get_sessions_count(node_key=None, only_active_sessions=False):
    if only_active_sessions:
        query = filter_active_sessions()
    else:
        query = Session.query

    if node_key:
        query = query.filter(Session.node_key == node_key)

    return query.count()


def get_sessions_count_by_service_type(node_key, service_type):
    query = Session.query.with_entities(func.count()).filter(
        Session.node_key == node_key,
        Session.service_type == service_type
    )
    return query.scalar()


def get_average_session_time():
    sql = text("""select
    AVG(TIME_TO_SEC(TIMEDIFF(client_updated_at, created_at)))
    as averageDuration FROM session;""")
    result = db.engine.execute(sql)
    myrow = result.fetchone()
    seconds = int(myrow[0]) if myrow[0] is not None else 0
    return timedelta(seconds=seconds)


def get_total_data_transferred():
    sql = text("""select SUM(client_bytes_sent) as clientBytesSent,
    SUM(client_bytes_received) as clientBytesReceived FROM session;""")
    result = db.engine.execute(sql)
    myrow = result.fetchone()
    total_bytes = (myrow[0] or 0) + (myrow[1] or 0)
    return total_bytes


def get_total_data_transferred_by_node(node_key, service_type):
    sql = text("""
        SELECT
        SUM(client_bytes_sent) AS clientBytesSent,
        SUM(client_bytes_received) AS clientBytesReceived
        FROM session
        WHERE node_key=:node_key AND service_type=:service_type;
        """)
    result = db.engine.execute(
        sql, node_key=node_key, service_type=service_type
    )
    myrow = result.fetchone()
    total_bytes = (myrow[0] or 0) + (myrow[1] or 0)
    return total_bytes


def get_country_string(country):
    return country or 'N/A'


def get_nodes(limit=None):
    nodes = Node.query.order_by(Node.updated_at.desc())

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
        node.last_seen = delta.total_seconds()
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
        node.last_seen = delta.total_seconds()
    return nodes


def get_node_status(node):
    return 'Online' if node.is_active() else 'Offline'


def get_node_info(node_key, service_type):
    node = Node.query.get([node_key, service_type])
    delta = datetime.utcnow() - node.updated_at
    node.last_seen = delta.total_seconds()
    node.country_string = get_country_string(
        node.get_country_from_service_proposal()
    )
    node.sessions = get_sessions(
        node_key=node_key,
        service_type=service_type,
        limit=10
    )
    node.data_transferred = get_total_data_transferred_by_node(
        node_key, service_type
    )
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
    se.duration = duration
    se.data_sent = se.client_bytes_sent
    se.data_received = se.client_bytes_received
    se.data_transferred = se.client_bytes_sent + se.client_bytes_received
    session_time = datetime.utcnow() - se.created_at
    se.started = session_time.total_seconds()
    se.status = 'Ongoing' if se.is_active() else 'Completed'
    se.client_country_string = get_country_string(se.client_country)


def get_sessions(node_key=None, service_type=None, limit=None):
    if node_key and service_type:
        sessions = Session.query.filter(
            Session.node_key == node_key,
            Session.service_type == service_type
        )
    else:
        sessions = Session.query

    sessions = sessions.order_by(Session.created_at.desc())

    if limit:
        sessions = sessions.limit(limit)

    sessions = sessions.all()

    for se in sessions:
        enrich_session_info(se)

    return sessions


def get_session_info(session_key):
    se = Session.query.get(session_key)
    if se is not None:
        enrich_session_info(se)
    return se


def get_sessions_country_stats():
    results = db.session.query(
        Session.client_country,
        func.count(Session.session_key).label('count')
    ).group_by(Session.client_country).order_by(desc('count')).all()

    return results
