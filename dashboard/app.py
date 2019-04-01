from dashboard.db_queries.leaderboard import (
    get_leaderboard_rows,
    enrich_leaderboard_rows
)
from dashboard.model_layer import (
    get_active_nodes_count,
    get_sessions_count,
    get_average_session_time,
    get_total_data_transferred,
    get_available_nodes,
    get_sessions,
    get_node_info,
    get_sessions_country_stats,
    get_nodes,
    get_session_info
)
from werkzeug.contrib.cache import SimpleCache
from dashboard.helpers import get_week_range
from flask import Flask, render_template
from datetime import datetime
from models import db
import settings
from models import db


app = Flask(__name__)
db.init_app(app)

cache = SimpleCache()


def _generate_database_uri(db_config):
    return 'mysql+pymysql://{}:{}@{}/{}'.format(
        db_config['user'], db_config['passwd'], db_config['host'],
        db_config['name'])


app.config['SQLALCHEMY_DATABASE_URI'] =\
    _generate_database_uri(settings.DB_CONFIG)


@app.route('/')
def main():
    page_content = cache.get('dashboard-page')
    if page_content is None:

        page_content = render_template(
            'dashboard.html',
            active_nodes_count=get_active_nodes_count(),
            sessions_count=get_sessions_count(),
            active_sessions_count=get_sessions_count(
                only_active_sessions=True
            ),
            average_session_time=get_average_session_time(),
            total_data_transferred=get_total_data_transferred(),
            available_nodes=get_available_nodes(limit=10),
            sessions=get_sessions(limit=10),
        )

        cache.set(
            'dashboard-page',
            page_content,
            timeout=1 * 60
        )

    return page_content


@app.route('/leaderboard')
def leaderboard():
    page_content = cache.get('leaderboard')
    if page_content is None:
        date_from, date_to = get_week_range(datetime.utcnow().date())
        leader_board_rows = get_leaderboard_rows(date_from, date_to, 10)
        enrich_leaderboard_rows(leader_board_rows, date_from, date_to)
        page_content = render_template(
            'leaderboard.html',
            date_from=date_from.strftime("%Y-%m-%d"),
            date_to=date_to.strftime("%Y-%m-%d"),
            leaderboard_rows=leader_board_rows,
        )
        cache.set(
            'leaderboard',
            page_content,
            timeout=1 * 60
        )

    return page_content


@app.route('/node/<key>/<service_type>')
def node(key, service_type):
    node = get_node_info(key, service_type)
    return render_template(
        'node.html',
        node=node,
    )


@app.route('/nodes')
def nodes():

    nodes = cache.get('all-nodes')
    if nodes is None:
        nodes = get_nodes(limit=500)
        cache.set(
            'all-nodes',
            nodes,
            timeout=1 * 60
        )

    return render_template(
        'nodes.html',
        nodes=nodes
    )


@app.route('/session/<key>')
def session(key):
    session = get_session_info(key)
    return render_template(
        'session.html',
        session=session,
    )


@app.route('/sessions')
def sessions():
    sessions = cache.get('all-sessions')
    if sessions is None:
        sessions = get_sessions(limit=500)
        cache.set(
            'all-sessions',
            sessions,
            timeout=1 * 60
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


def init_db(custom_config=None):
    if custom_config is not None:
        app.config['SQLALCHEMY_DATABASE_URI'] =\
            _generate_database_uri(custom_config)
    db.init_app(app)


if __name__ == '__main__':
    app.run(debug=True)
