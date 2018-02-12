"""migrate existing ips to country

Revision ID: 36d55d0bcbdd
Revises: 5692855d1037
Create Date: 2018-02-09 14:09:48.390475

"""
from alembic import op
import sqlalchemy as sa

from ip import detect_country
from models import db, Node, Session
from app import app


# revision identifiers, used by Alembic.
revision = '36d55d0bcbdd'
down_revision = '5692855d1037'
branch_labels = None
depends_on = None

db.init_app(app)


def upgrade():
    for node in Node.query.all():
        node.country = detect_country(node.ip) or ''
    for session in Session.query.all():
        session.client_country = detect_country(session.client_ip)
    db.session.commit()


def downgrade():
    pass
