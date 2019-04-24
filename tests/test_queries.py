from datetime import datetime

from tests.test_case import TestCase
from models import db, Node, Session, IdentityRegistration
from queries import filter_active_nodes, filter_active_sessions
from queries import filter_active_nodes_by_service_type
from queries import filter_nodes_in_bounty_programme
from queries import filter_nodes_by_node_type


class TestQueries(TestCase):
    def test_filter_active_nodes(self):
        node1 = Node("node1", "dummy")
        node1.mark_activity()
        db.session.add(node1)

        node2 = Node("node2", "dummy")
        db.session.add(node2)

        nodes = filter_active_nodes().all()
        self.assertEqual([node1], nodes)

    def test_filter_active_sessions(self):
        session1 = Session("session1", "openvpn")
        session1.client_updated_at = datetime.utcnow()
        db.session.add(session1)

        session2 = Session("session2", "openvpn")
        db.session.add(session2)

        sessions = filter_active_sessions().all()
        self.assertEqual([session1], sessions)

    def test_filter_active_nodes_by_service_type(self):
        dummy_node = Node("node1", "dummy")
        dummy_node.mark_activity()
        db.session.add(dummy_node)

        openvpn_node = Node("node3", "openvpn")
        openvpn_node.mark_activity()
        db.session.add(openvpn_node)

        dummy_nodes = filter_active_nodes_by_service_type("dummy").all()
        self.assertEqual([dummy_node], dummy_nodes)

        openvpn_nodes = filter_active_nodes_by_service_type(
            "openvpn"
        ).all()
        self.assertEqual([openvpn_node], openvpn_nodes)

    def test_filter_nodes_in_bounty_programme(self):
        dummy_node = Node("node1", "dummy")
        dummy_node.mark_activity()
        db.session.add(dummy_node)

        dummy_node_2 = Node("node2", "dummy")
        dummy_node_2.mark_activity()
        db.session.add(dummy_node_2)

        ir = IdentityRegistration("node1", "test")
        db.session.add(ir)

        nodes = filter_active_nodes()

        filtered = filter_nodes_in_bounty_programme(nodes).all()
        self.assertEqual([dummy_node], filtered)

    def test_filter_nodes_in_bounty_programme_with_no_registration(self):
        dummy_node = Node("node1", "dummy")
        dummy_node.mark_activity()
        db.session.add(dummy_node)

        dummy_node_2 = Node("node2", "dummy")
        dummy_node_2.mark_activity()
        db.session.add(dummy_node_2)

        nodes = filter_active_nodes()

        filtered = filter_nodes_in_bounty_programme(nodes).all()
        self.assertEqual([], filtered)

    def test_filter_nodes_by_node_type(self):
        dummy_node = Node("node1", "dummy")
        dummy_node.node_type = "some-type"
        dummy_node.mark_activity()
        db.session.add(dummy_node)

        dummy_node_2 = Node("node2", "dummy")
        dummy_node_2.mark_activity()
        db.session.add(dummy_node_2)

        nodes = filter_active_nodes()

        filtered = filter_nodes_by_node_type(nodes, "some-type").all()
        self.assertEqual([dummy_node], filtered)

    def test_filter_nodes_by_node_type_no_match(self):
        dummy_node = Node("node1", "dummy")
        dummy_node.mark_activity()
        db.session.add(dummy_node)

        dummy_node_2 = Node("node2", "dummy")
        dummy_node_2.mark_activity()
        db.session.add(dummy_node_2)

        nodes = filter_active_nodes()

        filtered = filter_nodes_by_node_type(nodes, "some-type").all()
        self.assertEqual([], filtered)
