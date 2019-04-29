import json
from models import db, Node, ProposalAccessPolicy
from tests.test_case import TestCase
from tests.utils import build_test_authorization, setting


class TestApi(TestCase):
    def test_restrict_by_ip_fail(self):
        payload = {}
        auth = build_test_authorization(json.dumps(payload))

        self._create_node(auth['public_address'], "openvpn")

        ips = [
            '1.1.1.1',
            '2.2.2.2',
        ]
        with setting('RESTRICT_BY_IP_ENABLED', True), \
                setting('ALLOWED_IP_ADDRESSES', ips):
            re = self._post(
                '/v1/ping_proposal',
                payload,
                headers=auth['headers']
            )

        self.assertEqual(403, re.status_code)
        self.assertEqual({'error': 'resource is forbidden'}, re.json)

    def test_restrict_by_ip_success(self):
        payload = {}
        auth = build_test_authorization(json.dumps(payload))

        self._create_node(auth['public_address'], "openvpn")

        ips = [
            '1.1.1.1',
            '2.2.2.2',
            self.REMOTE_ADDR,
        ]
        with setting('RESTRICT_BY_IP_ENABLED', True), \
                setting('ALLOWED_IP_ADDRESSES', ips):
            re = self._post(
                '/v1/ping_proposal',
                payload,
                headers=auth['headers']
            )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

    def _create_node(self, node_key, service_type, access_policy_id=None,
                     access_policy_source=None):
        node = Node(node_key, service_type)
        node.proposal = json.dumps({
            "id": 1,
            "format": "service-proposal/v1",
            "provider_id": node_key,
        })
        db.session.add(node)

        if access_policy_id and access_policy_source:
            item = ProposalAccessPolicy(node_key, access_policy_id,
                                        access_policy_source)
            db.session.add(item)

        return node
