"""Schedule event to refresh monthly leaderboard

Revision ID: e73480955f62
Revises: 8b81804f8861
Create Date: 2019-08-07 21:54:52.759443

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e73480955f62'
down_revision = '8b81804f8861'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute("""

    CREATE EVENT IF NOT EXISTS evt_refresh_dwh_leaderboard
    ON SCHEDULE
        EVERY 3 MINUTE
    COMMENT 'Refresh monthly leaderboard'
    DO
    BEGIN
        SET @service_type = 'openvpn',
            @node_type = 'residential',
            @date_from = DATE_FORMAT(NOW(), '%%Y-%%m-1 00:00:00'),
            @date_to = DATE_FORMAT(LAST_DAY(NOW()), '%%Y-%%m-%%d 23:59:59');
    
        DELETE FROM dwh_leaderboard_nodes WHERE 1 = 1;
    
        INSERT INTO
            dwh_leaderboard_nodes(provider_id, updated_at, service_type, node_type, country)
        SELECT
            ir.identity,
            n.updated_at,
            n.service_type,
            n.node_type,
            JSON_UNQUOTE(JSON_EXTRACT(n.proposal, '$.service_definition.location.country'))
        FROM
            identity_registration ir
                INNER JOIN node n ON n.node_key = ir.identity
        WHERE
              n.service_type = @service_type
          AND n.node_type = @node_type
          AND n.updated_at BETWEEN @date_from AND @date_to
          AND JSON_UNQUOTE(JSON_EXTRACT(n.proposal, '$.service_definition.location.country')) IN
              ('DE', 'GB', 'IT', 'US')
        LIMIT 0, 1000;
    
        DELETE FROM dwh_leaderboard_availability WHERE 1 = 1;
    
        INSERT INTO
            dwh_leaderboard_availability(provider_id, hours_available)
        SELECT
            av.node_key          AS provider_id,
            ROUND(COUNT(1) / 60) AS hours_available
        FROM
            node_availability av
                RIGHT JOIN dwh_leaderboard_nodes n ON n.provider_id = av.node_key
        WHERE
              av.service_type = @service_type
          AND av.date BETWEEN @date_from AND @date_to
        GROUP BY av.node_key
        LIMIT 0, 1000;
    
        DELETE FROM dwh_leaderboard_session_stats WHERE 1 = 1;
    
        INSERT INTO
            dwh_leaderboard_session_stats(provider_id, unique_users, sessions, data_transferred)
        SELECT
            s.node_key                                              AS provider_id,
            COUNT(DISTINCT (s.consumer_id))                         AS unique_users,
            COUNT(s.session_key)                                    AS sessions,
            SUM(s.client_bytes_sent) + SUM(s.client_bytes_received) AS data_transferred
        FROM
            session s
                RIGHT JOIN dwh_leaderboard_nodes n ON s.node_key = n.provider_id
        WHERE
              s.client_updated_at BETWEEN @date_from AND @date_to
          AND s.service_type = @service_type
        GROUP BY s.node_key
        LIMIT 0, 1000;
    
        DELETE FROM dwh_leaderboard WHERE provider_id NOT IN (SELECT provider_id FROM dwh_leaderboard_nodes);
    
        REPLACE INTO
            dwh_leaderboard (provider_id,
                             updated_at,
                             service_type,
                             node_type,
                             country,
                             hours_available,
                             unique_users,
                             sessions,
                             data_transferred)
        SELECT
            n.provider_id,
            n.updated_at,
            n.service_type,
            n.node_type,
            n.country,
            COALESCE(av.hours_available, 0),
            COALESCE(s.unique_users, 0),
            COALESCE(s.sessions, 0),
            COALESCE(s.data_transferred, 0)
        FROM
            dwh_leaderboard_nodes n
                LEFT JOIN dwh_leaderboard_availability av ON av.provider_id = n.provider_id
                LEFT JOIN dwh_leaderboard_session_stats s ON s.provider_id = n.provider_id
        LIMIT 0, 1000;
    END
    """)


def downgrade():
    conn = op.get_bind()
    conn.execute("""

    DROP EVENT IF EXISTS evt_refresh_dwh_leaderboard;

    """)
