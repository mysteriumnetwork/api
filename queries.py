from datetime import datetime
from models import Node, Session, NODE_AVAILABILITY_TIMEOUT


def filter_active_nodes():
    return _filter_active_models(Node, 'updated_at')


def filter_active_sessions():
    return _filter_active_models(Session, 'client_updated_at')


def _filter_active_models(model, column):
    updated_timestamp = getattr(model, column)
    return model.query.filter(
        updated_timestamp >= datetime.utcnow() - NODE_AVAILABILITY_TIMEOUT
    )
