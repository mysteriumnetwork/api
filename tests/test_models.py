from datetime import datetime, timedelta
from tests.test_case import TestCase
from models import Session, Node, AVAILABILITY_TIMEOUT
import json


class TestSession(TestCase):
    def test_is_active(self):
        session = Session("session")

        self.assertFalse(session.is_active())

        session.client_updated_at = datetime.utcnow()
        self.assertTrue(session.is_active())

        timeout_delta = AVAILABILITY_TIMEOUT + timedelta(minutes=1)
        session.client_updated_at = datetime.utcnow() - timeout_delta
        self.assertFalse(session.is_active())


class TestNode(TestCase):
    def test_get_country_from_service_proposal(self):
        node = Node("key")
        node.proposal = json.dumps({
            "service_definition": {
                "location_originate": {"country": "country code"},
            },
        })
        self.assertEqual(
            "country code",
            node.get_country_from_service_proposal()
        )

    def test_get_country_from_empty_service_proposal(self):
        node = Node("key")
        node.proposal = json.dumps({})
        self.assertIsNone(node.get_country_from_service_proposal())

    def test_get_country_from_invalid_service_proposal(self):
        node = Node("key")
        node.proposal = json.dumps({
            "service_definition": {}
        })
        self.assertIsNone(node.get_country_from_service_proposal())

    def test_get_service_proposals_by_type(self):
        node = Node("key")
        node.proposal = json.dumps({
            "id": 1, "format": "service-proposal/v1", "provider_id": "node1"
        })
        node.service_type = "openvpn"
        res = node.get_service_proposals_by_type("openvpn")
        self.assertEqual(len(res), 1)

        node2 = Node("key")
        node2.proposal = json.dumps({
            "id": 1, "format": "service-proposal/v1", "provider_id": "node1"
        })
        res = node2.get_service_proposals_by_type("openvpn")
        self.assertEqual(len(res), 0)
