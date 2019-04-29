import helpers
import logging
import settings
from datetime import datetime
from flask import Flask, request, render_template, jsonify
from flask_migrate import Migrate
from werkzeug.debug import get_current_traceback
from ip import mask_ip_partially
from queries import (
    filter_active_nodes,
    filter_active_nodes_by_service_type,
    filter_nodes_without_access_policies,
    filter_nodes_by_access_policy,
    filter_nodes_in_bounty_programme,
    filter_nodes_by_node_type
)
from eth_utils.address import is_hex_address as is_valid_eth_address
from models import (
    db, Node, NodeAvailability, Session, Identity, IdentityRegistration
)
from request_helpers import validate_json, restrict_by_ip, recover_identity
from api.proposals import register_endpoints as register_proposal_endpoints

if not settings.DISABLE_LOGS:
    helpers.setup_logger()

app = Flask(__name__)

register_proposal_endpoints(app)


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


@app.route('/v1/unregister_proposal', methods=['POST'])
@restrict_by_ip
@validate_json
@recover_identity
def unregister_proposal(caller_identity):
    payload = request.get_json(force=True)

    service_type = payload.get('service_type', 'openvpn')

    node_key = payload.get('provider_id', None)
    if node_key is None:
        return jsonify(error='missing provider_id'), 400

    if node_key.lower() != caller_identity:
        message = 'provider_id does not match current identity'
        return jsonify(error=message), 403

    node = Node.query.get([node_key, service_type])
    if not node:
        return jsonify({}), 404

    node.mark_inactive()
    db.session.commit()

    return jsonify({})


@app.route('/v1/proposals', methods=['GET'])
def proposals():
    service_type = request.args.get('service_type', 'openvpn')
    if service_type == "all":
        nodes = filter_active_nodes()
    else:
        nodes = filter_active_nodes_by_service_type(service_type)

    node_key = request.args.get('node_key')
    if node_key:
        nodes = nodes.filter_by(node_key=node_key)

    if request.args.get('access_policy') != '*':
        id = request.args.get('access_policy[id]')
        source = request.args.get('access_policy[source]')
        if id or source:
            nodes = filter_nodes_by_access_policy(nodes, id, source)
        else:
            nodes = filter_nodes_without_access_policies(nodes)

    if request.args.get('bounty_only') == 'true':
        nodes = filter_nodes_in_bounty_programme(nodes)

    node_type_arg = request.args.get('node_type')
    if node_type_arg:
        nodes = filter_nodes_by_node_type(nodes, node_type_arg)

    service_proposals = []
    for node in nodes:
        service_proposals += node.get_service_proposals()

    return jsonify({'proposals': service_proposals})


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


# End Point to save identity
@app.route('/v1/identities', methods=['POST'])
@recover_identity
def save_identity(caller_identity):
    identity = Identity.query.get(caller_identity)
    if identity:
        return jsonify(error='identity already exists'), 403

    identity = Identity(caller_identity)
    db.session.add(identity)
    db.session.commit()

    return jsonify({})


# End Point which returns payout info next to identity
@app.route('/v1/identities/<identity_url_param>/payout', methods=['GET'])
@recover_identity
def payout_info(identity_url_param, caller_identity):
    if identity_url_param.lower() != caller_identity:
        return jsonify(error='no permission to access this identity'), 403

    record = IdentityRegistration.query.get(caller_identity)
    if not record:
        return jsonify(error='payout info for this identity not found'), 404

    return jsonify({'eth_address': record.payout_eth_address})


# End Point which creates or updates payout info next to identity
@app.route('/v1/identities/<identity_url_param>/payout', methods=['PUT'])
@validate_json
@recover_identity
def set_payout_info(identity_url_param, caller_identity):
    payload = request.get_json(force=True)

    payout_eth_address = payload.get('payout_eth_address', None)
    if payout_eth_address is None:
        msg = 'missing payout_eth_address parameter in body'
        return jsonify(error=msg), 400

    if identity_url_param.lower() != caller_identity:
        msg = 'no permission to modify this identity'
        return jsonify(error=msg), 403

    if not is_valid_eth_address(payout_eth_address):
        msg = 'payout_eth_address is not in Ethereum address format'
        return jsonify(error=msg), 400

    record = IdentityRegistration.query.get(caller_identity)
    if record:
        record.update(payout_eth_address)
        db.session.add(record)
    else:
        new_record = IdentityRegistration(caller_identity, payout_eth_address)
        db.session.add(new_record)

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
