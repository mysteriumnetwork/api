import json
from models import (db, Node, ProposalAccessPolicy)
from tests.test_case import TestCase
from tests.utils import (
    build_test_authorization,
    build_static_public_address,
    setting
)
from identity_contract import IdentityContractFake
from api import proposals as proposalEndpoints


class TestApi(TestCase):
    def test_register_proposal_successful(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "openvpn",
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        node = Node.query.get([public_address, "openvpn"])
        self.assertEqual(self.REMOTE_ADDR, node.ip)

    def test_register_proposal_saves_access_policy(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "openvpn",
                "access_policies": [
                    {
                        "id": "test policy",
                        "source": "http://trust-oracle/test-policy"
                    }
                ]
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        policy = ProposalAccessPolicy.query.get([
            public_address,
            "test policy",
            "http://trust-oracle/test-policy"
        ])
        self.assertIsNotNone(policy)

    def test_register_proposal_with_access_policy_succeeds_twice(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "openvpn",
                "access_policies": [
                    {
                        "id": "test policy",
                        "source": "http://trust-oracle/test-policy"
                    }
                ]
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)

        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])

        self.assertEqual(200, re.status_code)

    def test_register_multiple_proposals_successful(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "openvpn",
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "dummy",
            }
        }

        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        node_openvpn = Node.query.get([public_address, "openvpn"])
        self.assertIsNotNone(node_openvpn)

        node_dummy = Node.query.get([public_address, "dummy"])
        self.assertIsNotNone(node_dummy)

    def test_register_proposal_successful_with_dummy_type(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "dummy",
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        node = Node.query.get([public_address, "dummy"])
        self.assertEqual(self.REMOTE_ADDR, node.ip)
        self.assertEqual("dummy", node.service_type)

    def test_register_proposal_successful_with_node_type(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "dummy",
                "service_definition": {
                    "location": {
                        "node_type": "dummy_type"
                    }
                }
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        node = Node.query.get([public_address, "dummy"])
        self.assertEqual(self.REMOTE_ADDR, node.ip)
        self.assertEqual("dummy_type", node.node_type)

    def test_register_proposal_successful_with_invalid_definition(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "dummy",
                "service_definition": "test"
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        node = Node.query.get([public_address, "dummy"])
        self.assertEqual(self.REMOTE_ADDR, node.ip)
        self.assertEqual('data-center', node.node_type)

    def test_register_proposal_with_unknown_ip(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "openvpn",
            }
        }

        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'],
            remote_addr='127.0.0.1'
        )
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        node = Node.query.get([public_address, "openvpn"])
        self.assertEqual('127.0.0.1', node.ip)

    def test_register_proposal_unauthorized(self):
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": "incorrect",
                "service_type": "openvpn",
            }
        }

        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(403, re.status_code)
        self.assertEqual(
            {'error': 'provider_id does not match current identity'},
            re.json
        )
        self.assertIsNotNone(re.json)

    def test_register_proposal_missing_service_type(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'missing service_type'},
            re.json
        )
        self.assertIsNotNone(re.json)

    def test_register_proposal_missing_provider_id(self):
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "service_type": "openvpn",
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(True)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'missing provider_id'},
            re.json
        )
        self.assertIsNotNone(re.json)

    def test_register_proposal_with_invalid_json(self):
        re = self.client.post('/v1/register_proposal', data='{asd}')
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'payload must be a valid json'}, re.json)

    def test_register_proposal_with_string_json(self):
        # string is actually a valid json,
        # but endpoints rely on json being a dictionary
        re = self.client.post('/v1/register_proposal', data='"some string"')
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'payload must be a valid json'}, re.json)

    def test_register_proposal_with_array_json(self):
        # string is actually a valid json,
        # but endpoints rely on json being a dictionary
        re = self.client.post('/v1/register_proposal', data='[]')
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'payload must be a valid json'}, re.json)

    def test_register_proposal_with_unregistered_identity(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
            }
        }
        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(False)
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(403, re.status_code)
        self.assertEqual(
            {'error': 'identity is not registered'},
            re.json
        )

    def test_register_proposal_with_verification_disabled(self):
        public_address = build_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
                "service_type": "openvpn",
            }
        }

        auth = build_test_authorization(json.dumps(payload))
        proposalEndpoints.identity_contract = IdentityContractFake(False)
        with setting('DISCOVERY_VERIFY_IDENTITY', False):
            re = self._post(
                '/v1/register_proposal',
                payload,
                headers=auth['headers'])

        self.assertEqual(200, re.status_code)
        self.assertEqual(
            {},
            re.json
        )

    def test_unregister_proposal_successful(self):
        public_address = build_static_public_address()
        node = self._create_node(public_address, "openvpn")
        node.mark_activity()
        self.assertTrue(node.is_active())

        # unregister
        payload = {
            "provider_id": public_address
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/unregister_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        self.assertFalse(node.is_active())

    def test_unregister_proposal_multiple_types(self):
        public_address = build_static_public_address()
        node_openvpn = self._create_node(public_address, "openvpn")
        node_openvpn.mark_activity()
        self.assertTrue(node_openvpn.is_active())

        node_dummy = self._create_node(public_address, "dummy")
        node_dummy.mark_activity()
        self.assertTrue(node_dummy.is_active())

        # unregister
        payload = {
            "provider_id": public_address,
            "service_type": "dummy",
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/unregister_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        self.assertTrue(node_openvpn.is_active())
        self.assertFalse(node_dummy.is_active())

    def test_unregister_proposal_missing_provider(self):
        # unregister
        payload = {

        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/unregister_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'missing provider_id'}, re.json)

    def test_unregister_proposal_unauthorized(self):
        payload = {
            "provider_id": "incorrect"
        }

        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/unregister_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(403, re.status_code)
        self.assertIsNotNone(re.json)
        self.assertEqual(
            {'error': 'provider_id does not match current identity'},
            re.json
        )

    # TODO: DRY
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
