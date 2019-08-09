from sqlalchemy import text
from models import db, AVAILABILITY_TIMEOUT


class LeaderboardRow:
    def __init__(self, row, total_hours_in_range):
        self.provider_id = row.provider_id
        self.sessions_count = row.sessions
        self.total_bytes = row.data_transferred
        self.unique_users = row.unique_users
        self.country = row.country
        self.service_type = row.service_type
        self.availability = '{0} / {1} h'.format(
            row.hours_available, total_hours_in_range
        )
        if row.last_seen is not None and row.last_seen < AVAILABILITY_TIMEOUT.seconds:
            self.service_status = 'Online'
        else:
            self.service_status = 'Offline'

    def __repr__(self):
        return 'provider_id: {0}, sessions_count: {1}, ' \
               'total_bytes: {2}, unique_users: {3}' \
            .format(
            self.provider_id,
            self.sessions_count,
            self.total_bytes,
            self.unique_users,
        )


def get_leaderboard_rows(date_from, date_to):
    sql = text("""
        SELECT
            l.provider_id,
            l.service_type,
            l.node_type,
            l.country,
            l.hours_available,
            l.unique_users,
            l.sessions,
            l.data_transferred,
            n.updated_at,
            TIMESTAMPDIFF(SECOND, n.updated_at, NOW()) AS last_seen
        FROM dwh_leaderboard l
            LEFT JOIN node n ON n.node_key = l.provider_id
        ORDER BY l.data_transferred DESC
        """)
    rows = db.engine.execute(sql).fetchall()
    total_hours_in_range = round((date_to - date_from).total_seconds() / 3600)
    leaderboard_rows = [LeaderboardRow(r, total_hours_in_range) for r in rows]
    return leaderboard_rows
