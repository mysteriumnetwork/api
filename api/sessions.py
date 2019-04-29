from flask import request, jsonify
from request_helpers import validate_json, recover_identity
from datetime import datetime
from ip import mask_ip_partially
from models import db, Session


def register_endpoints(app):
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
