"""change node primary key to a composite

Revision ID: 6a151731efac
Revises: 0cce46ad632d
Create Date: 2018-11-06 13:13:24.966616

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6a151731efac'
down_revision = '0cce46ad632d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    ALTER TABLE node DROP PRIMARY KEY, ADD PRIMARY KEY(node_key, service_type);
    """)
    op.add_column('session', sa.Column('service_type', mysql.VARCHAR(length=255), server_default=sa.text("'openvpn'"), nullable=False))
    op.add_column('node_availability', sa.Column('service_type', mysql.VARCHAR(length=255), server_default=sa.text("'openvpn'"), nullable=False))

def downgrade():
    op.execute("""
    ALTER TABLE node DROP PRIMARY KEY, ADD PRIMARY KEY(node_key);
    """) 
    op.drop_column('session', 'service_type')
    op.drop_column('node_availability', 'service_type')
