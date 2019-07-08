from api.stats.db_queries.node_availability import get_node_hours_online
from api.stats.model_layer import get_country_string, get_node_status
from sqlalchemy import text
from models import db, Node


class LeaderboardRow:
    def __init__(self, provider_id, sessions_count, total_bytes, unique_users):
        self.provider_id = provider_id
        self.sessions_count = sessions_count
        self.total_bytes = total_bytes
        self.unique_users = unique_users
        self.availability = None
        self.data_transferred = None
        self.country = None
        self.service_status = None

    @staticmethod
    def from_sql_row(row):
        provider_id, sessions_count, total_bytes, unique_users = row
        return LeaderboardRow(
            provider_id,
            sessions_count,
            total_bytes,
            unique_users
        )

    def __repr__(self):
        return 'provider_id: {0}, sessions_count: {1}, ' \
               'total_bytes: {2}, unique_users: {3}'\
            .format(
                self.provider_id,
                self.sessions_count,
                self.total_bytes,
                self.unique_users,
            )


def get_leaderboard_rows(date_from, date_to, offset=0, limit=10):
    query = text("""
        SELECT ir.identity AS provider_id,
        COUNT(s.session_key) AS sessions_count,
        SUM(s.client_bytes_sent) + SUM(s.client_bytes_received) AS total_bytes,
        COUNT(DISTINCT(s.consumer_id)) AS unique_users
        FROM identity_registration ir
        INNER JOIN node n ON n.node_key = ir.identity
        INNER JOIN session s ON s.node_key = ir.identity
            AND s.service_type = n.service_type
        WHERE s.client_updated_at >= '{date_from}'
            AND s.client_updated_at <= '{date_to}'
            AND n.updated_at >= '{date_from}'
            AND n.updated_at <= '{date_to}'
            AND ir.bounty_program = TRUE
        GROUP BY ir.identity, n.node_key
        ORDER BY total_bytes DESC
        LIMIT {limit}
        OFFSET {offset}
        """.format(
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
    )
    rows = db.engine.execute(query).fetchall()
    leader_board_rows = []
    for row in rows:
        leader_board_row = LeaderboardRow.from_sql_row(row)
        leader_board_rows.append(leader_board_row)
    return leader_board_rows


def enrich_leaderboard_rows(rows, date_from, date_to):
    supportedTypes = ['openvpn', 'wireguard', 'noop']
    for row in rows:
        for t in supportedTypes:
            node = Node.query.get([row.provider_id, t])
            if node:
                break

        row.country = get_country_string(
            node.get_country_from_service_proposal()
        )
        row.service_status = get_node_status(node)
        hours_online = get_node_hours_online(
            row.provider_id,
            node.service_type,
            date_from,
            date_to
        )

        total_hours_in_range = round((date_to - date_from).total_seconds() / 3600)
        row.availability = '{0} / {1} h'.format(
            hours_online, total_hours_in_range
        )
        row.data_transferred = row.total_bytes
