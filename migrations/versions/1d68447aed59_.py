"""added bounty_program column to api

Revision ID: 1d68447aed59
Revises: 590a0526e987
Create Date: 2019-05-02 13:31:18.915788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d68447aed59'
down_revision = '590a0526e987'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('identity_registration', sa.Column('bounty_program', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('identity_registration', 'bounty_program')
