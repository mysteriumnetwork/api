"""Initial migration

Revision ID: 283079f3eba9
Revises: 
Create Date: 2018-02-14 13:11:57.483655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '283079f3eba9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('identity',
    sa.Column('identity', sa.String(length=42), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('identity')
    )
    op.create_table('node',
    sa.Column('node_key', sa.String(length=42), nullable=False),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.Column('country', sa.String(length=255), nullable=True),
    sa.Column('connection_config', sa.Text(), nullable=True),
    sa.Column('proposal', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('node_key')
    )
    op.create_table('node_availability',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('node_key', sa.String(length=42), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('session',
    sa.Column('session_key', sa.String(length=36), nullable=False),
    sa.Column('node_key', sa.String(length=42), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('node_updated_at', sa.DateTime(), nullable=True),
    sa.Column('client_updated_at', sa.DateTime(), nullable=True),
    sa.Column('node_bytes_sent', sa.BigInteger(), nullable=True),
    sa.Column('node_bytes_received', sa.BigInteger(), nullable=True),
    sa.Column('consumer_id', sa.String(length=42), nullable=True),
    sa.Column('client_bytes_sent', sa.BigInteger(), nullable=True),
    sa.Column('client_bytes_received', sa.BigInteger(), nullable=True),
    sa.Column('client_ip', sa.String(length=45), nullable=True),
    sa.Column('client_country', sa.String(length=255), nullable=True),
    sa.Column('established', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('session_key')
    )


def downgrade():
    op.drop_table('session')
    op.drop_table('node_availability')
    op.drop_table('node')
    op.drop_table('identity')
