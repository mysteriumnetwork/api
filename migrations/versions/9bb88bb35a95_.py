"""Rename custom indexes to default model index names

Revision ID: 9bb88bb35a95
Revises: f448930e4058
Create Date: 2019-04-10 13:39:35.607114

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '9bb88bb35a95'
down_revision = 'f448930e4058'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('node_fast_active_count_index', table_name='node')
    op.create_index(op.f('ix_node_updated_at'), 'node', ['updated_at'], unique=False)

    op.drop_index('session_fast_count_index', table_name='session')
    op.create_index(op.f('ix_session_client_updated_at'), 'session', ['client_updated_at'], unique=False)

    op.drop_index('session_fast_node_index', table_name='session')
    op.create_index(op.f('ix_session_node_key'), 'session', ['node_key'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_node_updated_at'), table_name='node')
    op.create_index('node_fast_active_count_index', 'node', ['updated_at'], unique=False)

    op.drop_index(op.f('ix_session_client_updated_at'), table_name='session')
    op.create_index('session_fast_count_index', 'session', ['client_updated_at'], unique=False)

    op.drop_index(op.f('ix_session_node_key'), table_name='session')
    op.create_index('session_fast_node_index', 'session', ['node_key'], unique=False)
