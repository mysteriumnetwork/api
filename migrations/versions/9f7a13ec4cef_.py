"""empty message

Revision ID: 9f7a13ec4cef
Revises: 90f976272da9
Create Date: 2018-01-08 11:27:42.117647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
import json

from models import db, Node
from app import app

revision = '9f7a13ec4cef'
down_revision = '90f976272da9'
branch_labels = None
depends_on = None

db.init_app(app)


def upgrade():
    for node in Node.query.all():
        proposal = parse_proposal(node.connection_config)
        proposal_string = json.dumps(proposal) if proposal else ''
        node.proposal = proposal_string

    db.session.commit()


def parse_proposal(string):
    try:
        data = json.loads(string)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    return data.get('service_proposal')


def downgrade():
    pass
