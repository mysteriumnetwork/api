from dashboard.db_queries.node_availability import get_node_hours_online
from dashboard.helpers import get_natural_size
from sqlalchemy import text
from models import db


class LeaderboardRow:
    def __init__(self, provider_id, sessions_count, total_bytes, unique_users):
        self.provider_id = provider_id
        self.sessions_count = sessions_count
        self.total_bytes = total_bytes
        self.unique_users = unique_users
        self.availability_openvpn = None
        self.availability_wireguard = None
        self.data_transferred = None

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


def get_leaderboard_rows(date_from, date_to, limit=10):
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
            AND s.client_updated_at < '{date_to}'
            AND n.updated_at >= '{date_from}'
            AND n.updated_at < '{date_to}'
        GROUP BY ir.identity, n.node_key
        ORDER BY total_bytes DESC
        LIMIT {limit}
        """.format(
            date_from=date_from.strftime("%Y-%m-%d %H:%M:%S"),
            date_to=date_to.strftime("%Y-%m-%d %H:%M:%S"),
            limit=limit
        )
    )
    rows = db.engine.execute(query).fetchall()
    leader_board_rows = []
    for row in rows:
        leader_board_row = LeaderboardRow.from_sql_row(row)
        leader_board_rows.append(leader_board_row)
    return leader_board_rows


def enrich_leaderboard_rows(rows, date_from, date_to):
    for row in rows:
        hours_online_openvpn = get_node_hours_online(
            row.provider_id,
            'openvpn',
            date_from,
            date_to
        )
        hours_online_wireguard = get_node_hours_online(
            row.provider_id,
            'wireguard',
            date_from,
            date_to
        )
        row.availability_openvpn = '{} / 168 h'.format(
            hours_online_openvpn
        )
        row.availability_wireguard = '{} / 168 h'.format(
            hours_online_wireguard
        )
        row.data_transferred = get_natural_size(
            row.total_bytes
        )
