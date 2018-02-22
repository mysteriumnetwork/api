from datetime import datetime

from tests.test_case import TestCase
from models import db, Node, Session
from queries import filter_active_nodes, filter_active_sessions


class TestQueries(TestCase):
    def test_filter_active_nodes(self):
        node1 = Node("node1")
        node1.mark_activity()
        db.session.add(node1)

        node2 = Node("node2")
        db.session.add(node2)

        nodes = filter_active_nodes().all()
        self.assertEqual([node1], nodes)

    def test_filter_active_sessions(self):
        session1 = Session("session1")
        session1.client_updated_at = datetime.utcnow()
        db.session.add(session1)

        session2 = Session("session2")
        db.session.add(session2)

        sessions = filter_active_sessions().all()
        self.assertEqual([session1], sessions)
