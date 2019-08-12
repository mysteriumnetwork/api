from sqlalchemy import text

from models import db, Node


def from_sql_row(row):
    node = Node(row.node_key, row.service_type)
    node.updated_at = row.updated_at
    node.country_string = row.country_string
    node.node_type = row.node_type
    node.last_seen = row.last_seen
    return node


def get_nodes():
    sql = text("""
        SELECT
            node.node_key,
            node.updated_at,
            TIMESTAMPDIFF(SECOND, node.updated_at, NOW()) AS last_seen,
            JSON_UNQUOTE(JSON_EXTRACT(node.proposal, "$.service_definition.location.country")) AS country_string,
            JSON_UNQUOTE(JSON_EXTRACT(node.proposal, "$.service_type")) AS service_type,
            node.node_type
        FROM node
        ORDER BY node.updated_at DESC
    """)
    rows = db.engine.execute(sql).fetchall()
    nodes = [from_sql_row(r) for r in rows]

    return nodes
