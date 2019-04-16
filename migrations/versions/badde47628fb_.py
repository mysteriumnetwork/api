"""Add foreign key between proposal_access_policy and node

Revision ID: badde47628fb
Revises: 80e5d044e3b9
Create Date: 2019-04-15 13:50:26.756780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'badde47628fb'
down_revision = '80e5d044e3b9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(None, 'proposal_access_policy', 'node', ['node_key'], ['node_key'])


def downgrade():
    op.drop_constraint(None, 'proposal_access_policy', type_='foreignkey')
