from datetime import datetime

from tests.test_case import TestCase
from models import db, Node, Session
from queries import filter_active_nodes, filter_active_sessions
from queries import get_active_nodes_by_service_type


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

    def test_get_active_nodes_by_service_type(self):
        dummy_node = Node("node1")
        dummy_node.mark_activity()
        dummy_node.service_type = "dummy"
        db.session.add(dummy_node)

        no_service_type_node = Node("node2")
        db.session.add(no_service_type_node)

        openvpn_node = Node("node3")
        openvpn_node.mark_activity()
        openvpn_node.service_type = "openvpn"
        db.session.add(openvpn_node)

        dummy_nodes = get_active_nodes_by_service_type("dummy").all()
        self.assertEqual([dummy_node], dummy_nodes)

        openvpn_nodes = get_active_nodes_by_service_type(
            "openvpn"
        ).all()
        self.assertEqual([openvpn_node], openvpn_nodes)
