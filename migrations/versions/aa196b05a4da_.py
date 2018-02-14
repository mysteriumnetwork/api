"""Increase length of node_availability.node_key

Revision ID: aa196b05a4da
Revises: 36d55d0bcbdd
Create Date: 2018-02-13 12:47:31.069157

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'aa196b05a4da'
down_revision = '36d55d0bcbdd'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('node_availability', 'node_key',
                    existing_type=mysql.VARCHAR(length=34),
                    type_=sa.String(length=42))


def downgrade():
    op.alter_column('node_availability', 'node_key',
                    existing_type=sa.String(length=42),
                    type_=mysql.VARCHAR(length=34))
