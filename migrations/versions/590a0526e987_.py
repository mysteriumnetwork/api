"""add node_type to node

Revision ID: 590a0526e987
Revises: badde47628fb
Create Date: 2019-04-23 14:42:14.417286

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '590a0526e987'
down_revision = 'badde47628fb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('node', sa.Column('node_type', mysql.VARCHAR(length=255), server_default=sa.text("'data-center'"), nullable=False))


def downgrade():
    op.drop_column('node', 'node_type')
