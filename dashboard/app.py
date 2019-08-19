import logging
from collections import defaultdict

from api.stats.db_queries.leaderboard import (
    get_leaderboard_rows,
)
from api.stats.model_layer import (
    get_active_nodes_count,
    get_sessions_count,
    get_average_session_time,
    get_total_data_transferred,
    get_available_nodes,
    get_node_info,
    get_sessions_country_stats,
)
from api.stats.node_list import get_nodes
from dashboard.settings import (
    METRICS_CACHE_TIMEOUT,
    VIEW_SESSIONS_CACHE_TIMEOUT
)
from api.settings import DB_CONFIG
from werkzeug.contrib.cache import SimpleCache
from dashboard.helpers import get_month_range
from flask import Flask, render_template, request, abort, jsonify
from datetime import datetime
from models import db
from dashboard.filters import initialize_filters
from dashboard.discovery_api import fetch_sessions, ApiError, fetch_session


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

cache = SimpleCache()

initialize_filters(app)


def _generate_database_uri(db_config):
    return 'mysql+pymysql://{}:{}@{}/{}'.format(
        db_config['user'], db_config['passwd'], db_config['host'],
        db_config['name'])


app.config['SQLALCHEMY_DATABASE_URI'] =\
    _generate_database_uri(DB_CONFIG)


def collect_metrics():
    metrics = cache.get('metrics')
    if metrics is None:
        metrics = {
            'active_nodes_count': get_active_nodes_count(),
            'sessions_count': get_sessions_count(),
            'active_sessions_count': get_sessions_count(
                only_active_sessions=True
            ),
            'average_session_time': get_average_session_time(),
            'total_data_transferred': get_total_data_transferred(),
        }
        cache.set(
            'metrics',
            metrics,
            timeout=METRICS_CACHE_TIMEOUT
        )
    return metrics


@app.route('/')
def main():
    available_nodes = list(get_available_nodes())

    available_nodes_count_by_country = defaultdict(int)
    seen = set()
    for n in available_nodes:
        if n.node_key not in seen:
            available_nodes_count_by_country[n.country_string] += 1
            seen.add(n.node_key)

    dashboard_data = {
        'available_nodes': available_nodes,
        'available_nodes_count_by_country': available_nodes_count_by_country
    }

    page_content = render_template(
        'dashboard.html',
        **collect_metrics(),
        **dashboard_data
    )
    return page_content


@app.route('/leaderboard')
def leaderboard():
    date_from, date_to = get_month_range(datetime.utcnow().date())
    leaderboard_rows = get_leaderboard_rows(date_from, date_to)
    page_data = {
        'date_from': date_from.strftime('%b %d, %Y'),
        'date_to': date_to.strftime('%b %d, %Y'),
        'leaderboard_rows': leaderboard_rows,
    }
    page_content = render_template(
        'leaderboard.html',
        **page_data,
    )
    return page_content


@app.route('/node/<key>/<service_type>')
def node(key, service_type):
    node = get_node_info(key, service_type)
    return render_template(
        'service.html',
        node=node,
    )


@app.route('/services')
def nodes():
    return render_template(
        'services.html',
        nodes=get_nodes()
    )


# TODO: change to `/sessions/<key>`
@app.route('/session/<key>')
def session(key):
    session = fetch_session(key)

    return render_template(
        'session.html',
        session=session,
    )


@app.route('/sessions')
def sessions():
    sessions = cache.get('all-sessions')
    if sessions is None:
        sessions = fetch_sessions(limit=500)
        cache.set(
            'all-sessions',
            sessions,
            timeout=VIEW_SESSIONS_CACHE_TIMEOUT
        )

    return render_template(
        'sessions.html',
        sessions=sessions
    )


@app.route('/sessions-country')
def sessions_country():
    results = get_sessions_country_stats()

    return render_template(
        'sessions-country.html',
        stats=results
    )


@app.route('/ping')
def ping():
    return jsonify({'status': 'ok'})


@app.errorhandler(ApiError)
def handle_api_error(e):
    logging.exception('Request to discovery failed')
    return 'Request to discovery failed', 503


def init_db():
    db.init_app(app)


if __name__ == '__main__':
    app.run(debug=True)
