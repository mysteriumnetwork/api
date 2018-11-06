from datetime import datetime
from app import init_db, db, app
from models import Node, Session


# Creates some sample model instances for testing purposes
def create_fixtures():
    node = _create_node()
    db.session.add(node)

    session = _create_session(node)
    db.session.add(session)

    db.session.commit()


def _create_node():
    node = Node("test node", "dummy")
    node.updated_at = datetime.utcnow()
    node.proposal = '{}'
    return node


def _create_session(node):
    session = Session("test session")
    session.node_key = node.node_key
    session.client_updated_at = datetime.utcnow()
    return session


if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        create_fixtures()
