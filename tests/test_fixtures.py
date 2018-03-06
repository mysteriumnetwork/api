from fixtures import create_fixtures


from models import Node, db, Session
from tests.test_case import TestCase


class TestFixtures(TestCase):
    def test_create_fixtures(self):
        create_fixtures()

        db.session.rollback()
        nodes = Node.query.all()
        self.assertEqual(1, len(nodes))
        node = nodes[0]
        self.assertEqual("test node", node.node_key)

        sessions = Session.query.all()
        self.assertEqual(1, len(sessions))
        session = sessions[0]
        self.assertEqual("test session", session.session_key)
        self.assertEqual(node.node_key, session.node_key)
        self.assertIsNotNone(session.client_updated_at)
