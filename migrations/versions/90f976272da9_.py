"""Rename node.connection_config

Revision ID: 90f976272da9
Revises: 3d7bcbbf6cc4
Create Date: 2018-01-08 10:48:14.069122

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90f976272da9'
down_revision = '3d7bcbbf6cc4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('node', sa.Column('proposal', sa.Text()))


def downgrade():
    op.drop_column('node', 'proposal')
