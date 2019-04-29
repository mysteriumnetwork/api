import helpers
import logging
import settings
from datetime import datetime
from flask import Flask, request, render_template, jsonify
from flask_migrate import Migrate
from werkzeug.debug import get_current_traceback
from ip import mask_ip_partially
from models import db, Node, NodeAvailability, Session
from request_helpers import validate_json, restrict_by_ip, recover_identity
from api.proposals import register_endpoints as register_proposal_endpoints
from api.identities import register_endpoints as register_identity_endpoints

if not settings.DISABLE_LOGS:
    helpers.setup_logger()

app = Flask(__name__)

register_proposal_endpoints(app)
register_identity_endpoints(app)


def _generate_database_uri(db_config):
    return 'mysql+pymysql://{}:{}@{}/{}'.format(
        db_config['user'], db_config['passwd'], db_config['host'],
        db_config['name'])


app.config['SQLALCHEMY_DATABASE_URI'] =\
    _generate_database_uri(settings.DB_CONFIG)


migrate = Migrate(app, db)


# TODO: move to authorization.py
@app.route('/', methods=['GET'])
def home():
    return render_template(
        'api.html',
    )


# Node and client should call this endpoint each minute.
@app.route('/v1/sessions/<session_key>/stats', methods=['POST'])
@validate_json
@recover_identity
def session_stats_create(session_key, caller_identity):
    payload = request.get_json(force=True)

    service_type = payload.get('service_type', 'openvpn')

    bytes_sent = payload.get('bytes_sent')
    if not isinstance(bytes_sent, int) or bytes_sent < 0:
        return jsonify(
            error='bytes_sent missing or value is not unsigned int'
        ), 400

    bytes_received = payload.get('bytes_received')
    if not isinstance(bytes_received, int) or bytes_received < 0:
        return jsonify(
            error='bytes_received missing or value is not unsigned int'
        ), 400

    provider_id = payload.get('provider_id')
    if not provider_id:
        return jsonify(error='provider_id missing'), 400

    session = Session.query.get(session_key)
    if session is None:
        consumer_country = payload.get('consumer_country', '')
        session = Session(session_key, service_type)
        ip = request.remote_addr
        session.client_ip = mask_ip_partially(ip)
        session.client_country = consumer_country
        session.consumer_id = caller_identity
        session.node_key = provider_id
    else:
        session.service_type = service_type

    if session.consumer_id != caller_identity:
        message = 'session identity does not match current one'
        return jsonify(error=message), 403

    if session.has_expired():
        return jsonify(
            error='session has expired'
        ), 400

    session.client_bytes_sent = bytes_sent
    session.client_bytes_received = bytes_received
    session.client_updated_at = datetime.utcnow()

    db.session.add(session)
    db.session.commit()

    return jsonify({})


# Node call this function each minute.
@app.route('/v1/ping_proposal', methods=['POST'])
# TODO: remove deprecated route when it's not used anymore
@app.route('/v1/node_send_stats', methods=['POST'])
@restrict_by_ip
@validate_json
@recover_identity
def ping_proposal(caller_identity):
    payload = request.get_json(force=True)
    service_type = payload.get('service_type', 'openvpn')

    node = Node.query.get([caller_identity, service_type])
    if not node:
        return jsonify(error='node key not found'), 400

    node.mark_activity()

    # add record to NodeAvailability
    na = NodeAvailability(caller_identity)
    na.service_type = service_type

    db.session.add(na)
    db.session.commit()

    return jsonify({})


# End Point example which recovers public address from signed payload
@app.route('/v1/me', methods=['GET'])
@recover_identity
def test_signed_payload(caller_identity):
    return jsonify({
        'identity': caller_identity
    })


@app.errorhandler(404)
def method_not_found(e):
    return jsonify(error='unknown API method'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(error='method not allowed'), 405


@app.errorhandler(Exception)
def handle_error(e):
    track = get_current_traceback(
        skip=1,
        show_hidden_frames=True,
        ignore_system_exceptions=False
    )
    logging.error(track.plaintext)
    return jsonify(error=str(e)), 500


def start_debug_app():
    init_db()
    app.run(debug=True)


def init_db():
    db.init_app(app)


if __name__ == '__main__':
    start_debug_app()
