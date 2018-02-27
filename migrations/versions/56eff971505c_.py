"""Remove country field from node

Revision ID: 56eff971505c
Revises: 283079f3eba9
Create Date: 2018-02-27 13:28:10.841945

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '56eff971505c'
down_revision = '283079f3eba9'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('node', 'country')


def downgrade():
    op.add_column('node', sa.Column('country', mysql.VARCHAR(length=255), nullable=True))
