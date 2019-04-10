"""Create proposal_access_policy table

Revision ID: 80e5d044e3b9
Revises: 9bb88bb35a95
Create Date: 2019-04-15 13:23:30.044240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80e5d044e3b9'
down_revision = '9bb88bb35a95'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('proposal_access_policy',
    sa.Column('node_key', sa.String(length=42), nullable=False),
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('node_key', 'id', 'source')
    )


def downgrade():
    op.drop_table('proposal_access_policy')
