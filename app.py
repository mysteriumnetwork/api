import binascii
import json
import helpers
import logging
import base64
import settings
from datetime import datetime
from flask import Flask, request, render_template, jsonify
from flask_migrate import Migrate
from werkzeug.debug import get_current_traceback
from functools import wraps
from ip import mask_ip_partially
from queries import filter_active_nodes, filter_active_nodes_by_service_type
from identity_contract import IdentityContract
from eth_utils.address import is_hex_address as is_valid_eth_address
from signature import (
    recover_public_address,
    ValidationError as SignatureValidationError
)
from models import (
    db, Node, Session, NodeAvailability, Identity, IdentityRegistration
)

if not settings.DISABLE_LOGS:
    helpers.setup_logger()

app = Flask(__name__)


def _generate_database_uri(db_config):
    return 'mysql+pymysql://{}:{}@{}/{}'.format(
        db_config['user'], db_config['passwd'], db_config['host'],
        db_config['name'])


app.config['SQLALCHEMY_DATABASE_URI'] =\
    _generate_database_uri(settings.DB_CONFIG)


migrate = Migrate(app, db)

identity_contract = IdentityContract(
    settings.ETHER_RPC_URL,
    settings.IDENTITY_CONTRACT,
    settings.ETHER_MINING_MODE
)


def is_json_dict(data):
    try:
        json_data = json.loads(data)
    except ValueError:
        return False
    if not isinstance(json_data, dict):
        return False
    return True


def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        if not is_json_dict(request.data):
            return jsonify({"error": 'payload must be a valid json'}), 400
        return f(*args, **kw)
    return wrapper


# TODO: move to authorization.py
def decode_authorization_header(headers):
    # Authorization request header format:
    # Authorization: Signature <signature_base64_encoded>
    authorization = headers.get('Authorization')
    if not authorization:
        raise ValueError('missing Authorization in request header')

    authorization_parts = authorization.split(' ')
    if len(authorization_parts) != 2:
        raise ValueError('invalid Authorization header value provided, correct'
                         ' format: Signature <signature_base64_encoded>')

    authentication_type, signature_base64_encoded = authorization_parts

    if authentication_type != 'Signature':
        raise ValueError('authentication type have to be Signature')

    if signature_base64_encoded == '':
        raise ValueError('signature was not provided')

    try:
        signature_bytes = base64.b64decode(signature_base64_encoded)
    except binascii.Error as err:
        raise ValueError('signature must be base64 encoded: {0}'.format(err))

    try:
        return recover_public_address(
            request.data,
            signature_bytes,
        ).lower()
    except SignatureValidationError as err:
        raise ValueError('invalid signature format: {0}'.format(err))


def recover_identity(f):
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            caller_identity = decode_authorization_header(request.headers)
        except ValueError as err:
            return jsonify(error=str(err)), 401

        kw['caller_identity'] = caller_identity
        return f(*args, **kw)

    return wrapper


def restrict_by_ip(f):
    @wraps(f)
    def wrapper(*args, **kw):
        if settings.RESTRICT_BY_IP_ENABLED:
            if request.remote_addr not in settings.ALLOWED_IP_ADDRESSES:
                return jsonify(error='resource is forbidden'), 403

        return f(*args, **kw)

    return wrapper


@app.route('/', methods=['GET'])
def home():
    return render_template(
        'api.html',
    )


@app.route('/v1/register_proposal', methods=['POST'])
# TODO: remove deprecated route when it's not used anymore
@app.route('/v1/node_register', methods=['POST'])
@restrict_by_ip
@validate_json
@recover_identity
def register_proposal(caller_identity):
    if settings.DISCOVERY_VERIFY_IDENTITY and \
            not identity_contract.is_registered(caller_identity):
        return jsonify(error='identity is not registered'), 403

    payload = request.get_json(force=True)

    proposal = payload.get('service_proposal', None)
    if proposal is None:
        return jsonify(error='missing service_proposal'), 400

    service_type = proposal.get('service_type', None)
    if service_type is None:
        return jsonify(error='missing service_type'), 400

    node_key = proposal.get('provider_id', None)
    if node_key is None:
        return jsonify(error='missing provider_id'), 400

    if node_key.lower() != caller_identity:
        message = 'provider_id does not match current identity'
        return jsonify(error=message), 403

    node = Node.query.get([node_key, service_type])
    if not node:
        node = Node(node_key, service_type)

    node.ip = request.remote_addr
    node.proposal = json.dumps(proposal)

    # add these columns to make querying easier
    node.service_type = service_type
    node.access_list = proposal.get('access_list')

    node.mark_activity()
    db.session.add(node)
    db.session.commit()

    return jsonify({})


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

    access_list = request.args.get('access_list')
    if access_list:
        filtered = access_list if access_list != 'null' else None
        nodes = nodes.filter_by(access_list=filtered)

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
