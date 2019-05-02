from flask import jsonify, request, abort

from api.stats.model_layer import get_sessions, get_session_info


DEFAULT_SESSIONS_LIMIT = 100
MAX_SESSIONS_LIMIT = 500


def register_endpoints(app):
    @app.route('/v1/statistics/sessions', methods=['GET'])
    def sessions():
        limit = DEFAULT_SESSIONS_LIMIT
        if 'limit' in request.args:
            limit = int(request.args.get('limit'))
            if limit > MAX_SESSIONS_LIMIT:
                return jsonify({'error': 'Too many sessions requested'}), 400

        sessions = get_sessions(limit=limit)
        serialized = list(map(serialize_enriched_session, sessions))

        return jsonify({
            'sessions': serialized
        })

    @app.route('/v1/statistics/sessions/<key>')
    def session(key):
        session = get_session_info(key)
        if session is None:
            abort(404)
            return
        return jsonify({'session': serialize_enriched_session(session)})


def serialize_enriched_session(session):
    return {
        'session_key': session.session_key,
        'duration': round(session.duration.total_seconds()),
        'data_sent': session.data_sent,
        'data_received': session.data_received,
        'data_transferred': session.data_transferred,
        'started': session.started,
        'status': session.status,
        'client_country_string': session.client_country_string
    }
