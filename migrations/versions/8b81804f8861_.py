"""Data warehousing tables for leaderboard

Revision ID: 8b81804f8861
Revises: 22dafaa1f597
Create Date: 2019-08-07 15:07:28.737036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b81804f8861'
down_revision = '22dafaa1f597'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS dwh_leaderboard
    (
        provider_id      VARCHAR(42) PRIMARY KEY,
        updated_at       DATETIME,
        service_type     VARCHAR(255),
        node_type        VARCHAR(255),
        country          VARCHAR(20),
        hours_available  SMALLINT UNSIGNED,
        unique_users     INT UNSIGNED,
        sessions         INT UNSIGNED,
        data_transferred BIGINT UNSIGNED
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS dwh_leaderboard_nodes
    (
        provider_id  VARCHAR(42) PRIMARY KEY,
        updated_at   DATETIME,
        service_type VARCHAR(255),
        node_type    VARCHAR(255),
        country      VARCHAR(20)
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS dwh_leaderboard_availability
    (
        provider_id     VARCHAR(42) PRIMARY KEY,
        hours_available SMALLINT UNSIGNED
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS dwh_leaderboard_session_stats
    (
        provider_id      VARCHAR(42) PRIMARY KEY,
        unique_users     INT UNSIGNED,
        sessions         INT UNSIGNED,
        data_transferred BIGINT UNSIGNED
    );
    """)


def downgrade():
    conn = op.get_bind()
    conn.execute("""

    DROP TABLE IF EXISTS dwh_leaderboard;
    DROP TABLE IF EXISTS dwh_leaderboard_nodes;
    DROP TABLE IF EXISTS dwh_leaderboard_availability;
    DROP TABLE IF EXISTS dwh_leaderboard_session_stats;

    """)
