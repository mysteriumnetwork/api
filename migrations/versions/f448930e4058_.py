"""create table identity_registration

Revision ID: f448930e4058
Revises: 6a151731efac
Create Date: 2019-03-04 15:50:52.395995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f448930e4058'
down_revision = '6a151731efac'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'identity_registration',
        sa.Column('identity', sa.String(length=42), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('payout_eth_address', sa.String(length=42), nullable=True),
        sa.PrimaryKeyConstraint('identity')
    )


def downgrade():
    op.drop_table('identity_registration')
