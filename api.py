from flask import Flask, request, render_template, jsonify
from models import db, Node, Session
import json
from datetime import datetime
import helpers


helpers.setup_logger()
app = Flask(__name__)
db.init_app(app)


@app.route('/', methods=['GET'])
def home():
    return render_template(
        'api.html',
    )


@app.route('/v1/node_register', methods=['POST'])
def node_register():
    #payload = json.loads(request.data)
    payload = request.get_json(force=True)
    node_key = payload['node_key']
    connection_config = payload['connection_config']

    node = Node.query.get(node_key)
    if not node:
        node = Node(node_key)

    node.ip = request.remote_addr
    node.connection_config = connection_config
    node.updated_at = datetime.utcnow()
    db.session.add(node)
    db.session.commit()

    return jsonify({'status': 'ok'})


@app.route('/v1/client_create_session', methods=['POST'])
def client_create_session():
    payload = request.get_json(force=True)
    node_key = payload['node_key']

    node = Node.query.get(node_key)

    if not node:
        return json.dumps({'status': 'node key not found'})

    session_key = helpers.generate_random_string()
    session = Session(session_key)
    session.node_key = node_key
    session.client_updated_at = datetime.utcnow()
    session.client_ip = request.remote_addr

    db.session.add(session)
    db.session.commit()

    return jsonify(
    {
        'status': 'ok',
        'session_key': session_key,
        'connection_config': node.connection_config,
        #'node_ip': node.ip,
    })


@app.route('/v1/node_get_session', methods=['POST'])
def node_get_session():
    payload = request.get_json(force=True)
    node_key = payload['node_key']
    client_ip = payload['client_ip']

    node = Node.query.get(node_key)
    if not node:
        return json.dumps({'status': 'node key not found'})

    session = Session.query.filter_by(node_key=node_key, client_ip=client_ip, established=False).first()

    if session:
        session.established = True
        session.node_updated_at = datetime.utcnow()
        db.session.add(session)
        db.session.commit()

    return jsonify(
    {
        'status': 'ok',
        'session_key': session.session_key if session else None,
        'is_session_valid': session is not None
    })


# Node call this function each minute.
@app.route('/v1/node_send_stats', methods=['POST'])
def node_send_stats():
    payload = request.get_json(force=True)
    node_key = payload['node_key']
    sessions = payload['sessions']

    return_values = []

    node = Node.query.get(node_key)
    if not node:
        return json.dumps({'status': 'node key not found'})

    # update node updated_at
    node.updated_at = datetime.utcnow()
    db.session.add(node)
    db.session.commit()

    # update sessions
    for se in sessions:
        session_key = se['session_key']
        bytes_sent = se['bytes_sent']
        bytes_received = se['bytes_received']

        # get session by key
        session = Session.query.get(session_key)
        is_session_valid = False

        if not session:
            #logger.warning('session key not found')
            pass

        if session:
            if session.established:
                session.node_bytes_sent = bytes_sent
                session.node_bytes_received = bytes_received
                session.node_updated_at = datetime.utcnow()
                db.session.add(session)
                db.session.commit()
                is_session_valid = True

        return_values.append({
            'session_key': session_key,
            'is_session_valid': is_session_valid
        })

    return jsonify(
    {
        'status': 'ok',
        'sessions': return_values
    })


# Client call this function each minute.
@app.route('/v1/client_send_stats', methods=['POST'])
def client_send_stats():
    payload = request.get_json(force=True)
    session_key = payload['session_key']
    bytes_sent = payload['bytes_sent']
    bytes_received = payload['bytes_received']

    # get session by key
    session = Session.query.get(session_key)
    is_session_valid = False

    if not session:
        return json.dumps({'status': 'session key not found'})

    if session:
        if session.established:
            session.client_bytes_sent = bytes_sent
            session.client_bytes_received = bytes_received
            session.client_updated_at = datetime.utcnow()
            db.session.add(session)
            db.session.commit()
            is_session_valid = True

    return jsonify(
    {
        'status': 'ok',
        'session_key': session_key,
        'is_session_valid': is_session_valid
    })


if __name__ == '__main__':
    app.run(debug=True)

