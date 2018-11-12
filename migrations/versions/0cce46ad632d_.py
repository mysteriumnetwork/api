"""add indices

Revision ID: 0cce46ad632d
Revises: 7eaa506f41dc
Create Date: 2018-11-06 11:54:11.473467

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0cce46ad632d'
down_revision = '7eaa506f41dc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('session_fast_count_index', 'session', ['client_updated_at'], unique=False)
    op.create_index('node_availability_fast_stats_index', 'node_availability', ['node_key', 'date'], unique=False)
    op.create_index('node_fast_active_count_index', 'node', ['updated_at'], unique=False)
    op.create_index('session_fast_node_index', 'session', ['node_key'], unique=False)


def downgrade():
    op.drop_index('node_fast_active_count_index', table_name='node')
    op.drop_index('node_availability_fast_stats_index', table_name='node_availability')
    op.drop_index('session_fast_count_index', table_name='session')
    op.drop_index('session_fast_node_index', table_name='session')

