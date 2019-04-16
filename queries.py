from datetime import datetime
from models import Node, Session, AVAILABILITY_TIMEOUT, ProposalAccessPolicy
from sqlalchemy import func, distinct


def get_active_nodes_count_query():
    updated_timestamp = getattr(Node, 'updated_at')
    return Node.query.with_entities(
        func.count(distinct(Node.node_key))
    ).filter(
        updated_timestamp >= datetime.utcnow() - AVAILABILITY_TIMEOUT
    )


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
    return filter_active_nodes().filter(
        getattr(Node, 'service_type') == service_type
    )


def filter_nodes_by_access_policy(
        nodes: any, access_policy_id: str, access_policy_source: str) -> any:
    return nodes \
        .join(ProposalAccessPolicy) \
        .filter(ProposalAccessPolicy.id == access_policy_id
                and ProposalAccessPolicy.source == access_policy_source)


def filter_nodes_without_access_policies(nodes):
    return nodes \
        .outerjoin(ProposalAccessPolicy) \
        .filter(~Node.access_policies.any())
