"""Increase session.session_key length

Revision ID: 3d7bcbbf6cc4
Revises: 429ea5e0bc3a
Create Date: 2017-12-29 12:24:43.096982

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3d7bcbbf6cc4'
down_revision = '429ea5e0bc3a'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('session', 'session_key',
               existing_type=mysql.VARCHAR(length=34),
               type_=sa.String(length=36),
               nullable=False)


def downgrade():
    op.alter_column('session', 'session_key',
               existing_type=sa.String(length=36),
               type_=mysql.VARCHAR(length=34),
               nullable=False)
