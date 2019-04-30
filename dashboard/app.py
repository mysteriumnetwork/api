from api.stats.db_queries.leaderboard import (
    get_leaderboard_rows,
    enrich_leaderboard_rows
)
from api.stats.model_layer import (
    get_active_nodes_count,
    get_sessions_count,
    get_average_session_time,
    get_total_data_transferred,
    get_available_nodes,
    get_node_info,
    get_sessions_country_stats,
    get_nodes
)
from api.settings import DB_CONFIG
from werkzeug.contrib.cache import SimpleCache
from dashboard.helpers import get_week_range
from flask import Flask, render_template, request, abort, jsonify
from datetime import datetime
from models import db
from dashboard.filters import initialize_filters
from dashboard.discovery_api import fetch_sessions, ApiError, fetch_session


app = Flask(__name__)
db.init_app(app)

cache = SimpleCache()
LEADERBOARD_ROWS_PER_PAGE = 10

initialize_filters(app)


def _generate_database_uri(db_config):
    return 'mysql+pymysql://{}:{}@{}/{}'.format(
        db_config['user'], db_config['passwd'], db_config['host'],
        db_config['name'])


app.config['SQLALCHEMY_DATABASE_URI'] =\
    _generate_database_uri(DB_CONFIG)


@app.route('/')
def main():
    page_content = cache.get('dashboard-page')
    if page_content is None:
        try:
            sessions = fetch_sessions(10)
        except ApiError:
            abort(503)
            return
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
            sessions=sessions,
        )

        cache.set(
            'dashboard-page',
            page_content,
            timeout=1  # TODO: re-enable cache
        )

    return page_content


@app.route('/leaderboard')
def leaderboard():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        abort(400)
        return

    if page < 1:
        abort(400)
        return

    # TODO: return http error for non-existing pages

    cache_key = 'leaderboard-page-{}'.format(page)
    page_content = cache.get(cache_key)
    if page_content is None:
        offset = (page - 1) * LEADERBOARD_ROWS_PER_PAGE
        date_from, date_to = get_week_range(datetime.utcnow().date())
        leaderboard_rows = get_leaderboard_rows(
            date_from, date_to, offset=offset, limit=LEADERBOARD_ROWS_PER_PAGE
        )
        enrich_leaderboard_rows(leaderboard_rows, date_from, date_to)

        previous_page = None
        if page >= 2:
            previous_page = page - 1

        next_page = None
        # This is not always correct - i.e.
        # if we have 10 rows and we're in first page,
        # next button should be disabled.
        # TODO: find optimal way to get total rows count
        if len(leaderboard_rows) == LEADERBOARD_ROWS_PER_PAGE:
            next_page = page + 1

        page_content = render_template(
            'leaderboard.html',
            date_from=date_from.strftime('%b %d, %Y'),
            date_to=date_to.strftime('%b %d, %Y'),
            leaderboard_rows=leaderboard_rows,
            previous_page=previous_page,
            next_page=next_page,
            offset=offset
        )

        cache.set(
            cache_key,
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


# TODO: change to `/sessions/<key>`
@app.route('/session/<key>')
def session(key):
    try:
        session = fetch_session(key)
    except ApiError:
        abort(503)
        return

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


@app.route('/ping')
def ping():
    return jsonify({'status': 'ok'})


def init_db():
    db.init_app(app)


if __name__ == '__main__':
    app.run(debug=True)
