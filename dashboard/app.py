from flask import Flask, render_template
import model_layer
from werkzeug.contrib.cache import SimpleCache
import settings

app = Flask(__name__)
model_layer.db.init_app(app)

cache = SimpleCache()

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    settings.USER, settings.PASSWD, settings.DB_HOST, settings.DB_NAME)


@app.route('/')
def main():
    page_content = cache.get('dashboard-page')
    if page_content is None:

        page_content = render_template(
            'dashboard.html',
            active_nodes_count=model_layer.get_active_nodes_count(),
            sessions_count=model_layer.get_sessions_count(),
            average_session_time=model_layer.get_average_session_time(),
            total_data_transferred=model_layer.get_total_data_transferred(),
            nodes=model_layer.get_nodes(limit=10),
            available_nodes=model_layer.get_available_nodes(limit=10),
            sessions=model_layer.get_sessions(limit=10),
        )

        cache.set(
            'dashboard-page',
            page_content,
            timeout=1 * 60
        )

    return page_content


@app.route('/node/<key>')
def node(key):
    node = model_layer.get_node_info(key)
    return render_template(
        'node.html',
        node=node,
    )


@app.route('/nodes')
def nodes():

    nodes = cache.get('all-nodes')
    if nodes is None:
        nodes = model_layer.get_nodes(limit=500)
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
    session = model_layer.get_session_info(key)
    return render_template(
        'session.html',
        session=session,
    )


@app.route('/sessions')
def sessions():
    sessions = cache.get('all-sessions')
    if sessions is None:
        sessions = model_layer.get_sessions(limit=500)
        cache.set(
            'all-sessions',
            sessions,
            timeout=1 * 60
        )

    return render_template(
        'sessions.html',
        sessions=sessions
    )


if __name__ == '__main__':
    app.run(debug=True)
