from datetime import datetime
from models import Node, Session, AVAILABILITY_TIMEOUT
from models import ProposalAccessPolicy, IdentityRegistration, MonitoringFailed
from sqlalchemy import func, distinct
from typing import Optional


def get_active_nodes_count_query():
    updated_timestamp = getattr(Node, 'updated_at')
    return Node.query.with_entities(
        func.count(distinct(Node.node_key))
    ).filter(
        updated_timestamp >= datetime.utcnow() - AVAILABILITY_TIMEOUT
    )


def filter_active_nodes():
    return _filter_active_models(Node, 'updated_at').order_by(
        Node.node_key.asc(),
        Node.service_type.asc()
    )


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


def filter_nodes_by_access_policy(nodes: any, access_policy_id: Optional[str],
                                  access_policy_source: Optional[str]) -> any:
    if not access_policy_id and not access_policy_source:
        return nodes

    nodes = nodes.join(ProposalAccessPolicy)
    if access_policy_id:
        nodes = nodes.filter(ProposalAccessPolicy.id == access_policy_id)
    if access_policy_source:
        nodes = nodes.filter(
            ProposalAccessPolicy.source == access_policy_source)

    return nodes


def filter_nodes_without_access_policies(nodes):
    return nodes \
        .outerjoin(ProposalAccessPolicy) \
        .filter(~Node.access_policies.any())


def filter_nodes_in_bounty_programme(nodes):
    return nodes \
        .join(
            IdentityRegistration, Node.node_key == IdentityRegistration.identity
        ).filter(IdentityRegistration.payout_eth_address != "")


def filter_nodes_by_node_type(nodes, node_type):
    return nodes.filter(Node.node_type == node_type)


def filter_nodes_by_monitoring_failed(nodes):
    return nodes.outerjoin(MonitoringFailed).filter(~Node.monitoring_failed.any())
