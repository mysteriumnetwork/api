from flask import jsonify, request

from api.stats.model_layer import get_sessions


def register_endpoints(app):
    @app.route('/v1/statistics/sessions', methods=['GET'])
    def session_statistics():
        limit = request.args.get('limit')

        sessions = get_sessions(limit=limit)
        serialized = list(map(serialize_enriched_session, sessions))

        return jsonify({
            'sessions': serialized
        }), 200


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
