from datetime import datetime
from models import Node, Session, AVAILABILITY_TIMEOUT


def filter_active_nodes():
    return _filter_active_models(Node, 'updated_at')


def filter_active_sessions():
    return _filter_active_models(Session, 'client_updated_at')


def _filter_active_models(model, column):
    updated_timestamp = getattr(model, column)
    return model.query.filter(
        updated_timestamp >= datetime.utcnow() - AVAILABILITY_TIMEOUT
    )


def filter_active_nodes_by_service_type(service_type):
    return Node.query.filter(
        getattr(Node, 'updated_at') >= datetime.utcnow() - AVAILABILITY_TIMEOUT
    ).filter(getattr(Node, 'service_type') == service_type)
