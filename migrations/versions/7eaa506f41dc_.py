"""Add service_type column to node

Revision ID: 7eaa506f41dc
Revises: 56eff971505c
Create Date: 2018-10-08 09:47:44.206268

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7eaa506f41dc'
down_revision = '56eff971505c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('node', sa.Column('service_type', mysql.VARCHAR(length=255), server_default=sa.text("'openvpn'"), nullable=False))

def downgrade():
    op.drop_column('node', 'service_type')
