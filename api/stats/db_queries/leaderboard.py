from api.stats.db_queries.node_availability import get_node_hours_online
from api.stats.model_layer import get_country_string, get_node_status
from sqlalchemy import text
from models import db, Node


class LeaderboardRow:
    def __init__(
            self, provider_id, sessions_count,
            total_bytes, unique_users, country, service_type):
        self.provider_id = provider_id
        self.sessions_count = sessions_count
        self.total_bytes = total_bytes
        self.unique_users = unique_users
        self.country = country
        self.service_type = service_type
        self.availability = None
        self.service_status = None

    @staticmethod
    def from_sql_row(row):
        return LeaderboardRow(
            row['provider_id'],
            row['sessions_count'],
            row['total_bytes'],
            row['unique_users'],
            row['country'].replace('"', ''),
            row['service_type']
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
        SELECT
            n.node_type,
            n.service_type,
            ir.identity AS provider_id,
            n.updated_at as node_updated_at,
            COUNT(s.session_key) AS sessions_count,
            COUNT(DISTINCT(s.consumer_id)) AS unique_users,
            (
                SUM(s.client_bytes_sent) + SUM(s.client_bytes_received)
            ) AS total_bytes,
            JSON_EXTRACT(
                n.proposal, "$.service_definition.location.country"
            ) AS country
        FROM identity_registration ir
        INNER JOIN node n ON n.node_key = ir.identity
        INNER JOIN session s ON s.node_key = ir.identity
            AND s.service_type = n.service_type
        WHERE
            s.client_updated_at BETWEEN :date_from AND :date_to
        GROUP BY ir.identity, n.node_key
        HAVING
            node_type = :node_type
            AND service_type = :service_type
            AND node_updated_at BETWEEN :date_from AND :date_to
            AND (
                country = 'US'
                OR country = 'GB'
                OR country = 'UK'
                OR country = 'IT'
            )
        ORDER BY total_bytes DESC
        LIMIT :limit
        OFFSET :offset
        """)

    rows = db.engine.execute(
        query,
        date_from=date_from,
        date_to=date_to,
        node_type='residential',
        service_type='openvpn',
        limit=limit,
        offset=offset,
    ).fetchall()

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

        row.service_status = get_node_status(node)
        hours_online = get_node_hours_online(
            row.provider_id,
            row.service_type,
            date_from,
            date_to
        )

        total_hours_in_range = round(
            (date_to - date_from).total_seconds() / 3600
        )
        row.availability = '{0} / {1} h'.format(
            hours_online, total_hours_in_range
        )
