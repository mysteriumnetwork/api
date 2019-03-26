from models import NodeAvailability
from sqlalchemy import func


def get_node_hours_online(node_key, service_type, date_from, date_to) -> int:
    query = NodeAvailability.query.with_entities(func.count()).filter(
        NodeAvailability.node_key == node_key,
        NodeAvailability.service_type == service_type,
        date_from <= NodeAvailability.date,
        NodeAvailability.date <= date_to
    )
    records_count = query.scalar()
    return int(round(records_count / 60.0))
