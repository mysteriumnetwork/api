import unittest
import json
from datetime import datetime, timedelta
from models import (
    db, Session, Node, ProposalAccessPolicy, NodeAvailability,
    AVAILABILITY_TIMEOUT, IdentityRegistration
)
from tests.test_case import TestCase
from tests.utils import build_test_authorization, setting


class TestApi(TestCase):
    def test_proposals(self):
        node1 = self._create_node("node1", "openvpn")
        node1.mark_activity()

        # node.updated_at == None
        self._create_node("node2", "openvpn")

        #  node.updated_at timeout passed
        node3 = self._create_node("node3", "openvpn")
        timeout_delta = AVAILABILITY_TIMEOUT + timedelta(minutes=1)
        node3.updated_at = datetime.utcnow() - timeout_delta

        db.session.commit()

        re = self._get('/v1/proposals')
        self.assertEqual(200, re.status_code)
        data = re.json
        proposals = data['proposals']
        self.assertEqual(1, len(proposals))
        self.assertIn('node1', proposals[0]['provider_id'])

    def test_proposals_filtering(self):
        node = self._create_sample_node()
        node.mark_activity()
        db.session.commit()

        re = self._get('/v1/proposals', {'node_key': 'node1'})

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertEqual(1, len(proposals))
        proposal = proposals[0]
        self.assertIsNotNone(proposal['id'])
        self.assertEqual('node1', proposal['provider_id'])

    def test_proposals_all(self):
        node = self._create_sample_node()
        node.mark_activity()
        node_noop = self._create_node("node2", "noop")
        node_noop.mark_activity()
        db.session.commit()

        re = self._get('/v1/proposals', {'service_type': 'all'})

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertEqual(2, len(proposals))

    def test_proposals_filtering_service_type_openvpn(self):
        node = self._create_sample_node()
        node.mark_activity()
        db.session.commit()

        re = self._get('/v1/proposals', {'service_type': 'openvpn'})

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertEqual(1, len(proposals))
        proposal = proposals[0]
        self.assertIsNotNone(proposal['id'])
        self.assertEqual('node1', proposal['provider_id'])
        self.assertEqual(node.service_type, "openvpn")

    def test_proposals_filtering_service_type_string(self):
        node = self._create_sample_node()
        node.mark_activity()
        db.session.commit()

        re = self._get(
            '/v1/proposals',
            {'service_type': 'something else entirely'}
        )

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertEqual(0, len(proposals))

    def test_proposals_filtering_no_service_type(self):
        node = self._create_sample_node()
        node.mark_activity()
        db.session.commit()

        re = self._get(
            '/v1/proposals'
        )

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertEqual(1, len(proposals))
        proposal = proposals[0]
        self.assertIsNotNone(proposal['id'])
        self.assertEqual('node1', proposal['provider_id'])
        self.assertEqual(node.service_type, "openvpn")

    def test_proposals_with_unknown_node_key(self):
        self._create_sample_node()

        re = self._get('/v1/proposals', {'node_key': 'UNKNOWN'})

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual([], data['proposals'])

    def test_proposals_returns_all_proposals_without_policies(self):
        n1 = self._create_node("node1", "openvpn")
        n1.mark_activity()
        n2 = self._create_node("node2", "openvpn", "mysterium", "test source")
        n2.mark_activity()

        re = self._get(
            '/v1/proposals',
            {'service_type': 'all'}
        )

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual(1, len(data['proposals']))
        self.assertEqual('node1', data['proposals'][0]['provider_id'])

    def test_proposals_filtering_by_access_policy(self):
        n1 = self._create_node("node1", "openvpn")
        n1.mark_activity()
        n2 = self._create_node("node2", "openvpn", "mysterium", "test source")
        n2.mark_activity()
        n3 = self._create_node("node3", "openvpn", "private", "test source")
        n3.mark_activity()

        re = self._get(
            '/v1/proposals',
            {
                'service_type': 'all',
                'access_policy[id]': 'mysterium',
                'access_policy[source]': 'test source',
            }
        )

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual(1, len(data['proposals']))
        self.assertEqual('node2', data['proposals'][0]['provider_id'])

    def test_proposals_filtering_by_access_policy_single_param(self):
        n1 = self._create_node("node1", "openvpn")
        n1.mark_activity()
        n2 = self._create_node("node2", "openvpn", "mysterium", "test source")
        n2.mark_activity()

        re = self._get(
            '/v1/proposals',
            {
                'service_type': 'all',
                'access_policy[id]': 'mysterium'
            }
        )

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual(1, len(data['proposals']))
        self.assertEqual('node2', data['proposals'][0]['provider_id'])

    def test_proposals_filtering_bounty_only(self):
        n1 = self._create_node("node1", "openvpn")
        n1.mark_activity()
        n2 = self._create_node("node2", "openvpn")
        n2.mark_activity()

        self._create_identity_registration("node2", "some_address")

        re = self._get(
            '/v1/proposals',
            {
                'service_type': 'all',
                'bounty_only': 'true',
            }
        )

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual(1, len(data['proposals']))
        self.assertEqual('node2', data['proposals'][0]['provider_id'])

    def test_proposals_filtering_by_star_policy_returns_all_proposals(self):
        n1 = self._create_node("node1", "openvpn")
        n1.mark_activity()
        n2 = self._create_node("node2", "openvpn", "mysterium", "test source")
        n2.mark_activity()

        re = self._get(
            '/v1/proposals',
            {'service_type': 'all', 'access_policy': '*'}
        )

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual(2, len(data['proposals']))

    def test_proposals_filtering_by_node_type(self):
        n1 = self._create_node("node1", "openvpn")
        n1.node_type = "dummy_type"
        n1.mark_activity()
        n2 = self._create_node("node2", "openvpn", "mysterium", "test source")
        n2.mark_activity()

        re = self._get(
            '/v1/proposals',
            {'node_type': 'dummy_type'}
        )

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual(1, len(data['proposals']))

    def test_session_stats_create_without_session_record(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
            'consumer_country': 'country'
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        session = Session.query.get('123')
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertEqual(auth['public_address'], session.consumer_id)
        self.assertEqual('8.8.8.X', session.client_ip)
        self.assertEqual('country', session.client_country)
        self.assertEqual('0x1', session.node_key)
        self.assertEqual('openvpn', session.service_type)

    def test_session_stats_create_with_type(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
            'consumer_country': 'country',
            'service_type': 'dummy'
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        session = Session.query.get('123')
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertEqual(auth['public_address'], session.consumer_id)
        self.assertEqual('8.8.8.X', session.client_ip)
        self.assertEqual('country', session.client_country)
        self.assertEqual('0x1', session.node_key)
        self.assertEqual('dummy', session.service_type)

    def test_session_stats_without_session_record_and_consumer_country(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)
        session = Session.query.get('123')
        self.assertEqual('', session.client_country)

    def test_session_stats_create_without_session_record_with_unknown_ip(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
            remote_addr='127.0.0.1',
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        session = Session.query.get('123')
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertEqual(auth['public_address'], session.consumer_id)
        self.assertEqual('127.0.0.X', session.client_ip)
        self.assertEqual('', session.client_country)
        self.assertEqual('0x1', session.node_key)

    def test_session_stats_create_successful(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))

        session = Session('123', 'openvpn')
        session.consumer_id = auth['public_address']
        db.session.add(session)
        db.session.commit()

        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        session = Session.query.get('123')
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertIsNone(session.node_key)

    def test_session_stats_create_with_different_consumer_id(self):
        session = Session('123', 'openvpn')
        session.consumer_id = 'different'
        db.session.add(session)
        db.session.commit()

        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(403, re.status_code)
        self.assertEqual(
            {'error': 'session identity does not match current one'},
            re.json
        )

        session = Session.query.get('123')
        self.assertEqual(0, session.client_bytes_sent)

    def test_session_stats_create_with_negative_values(self):
        auth = build_test_authorization()
        re = self._post(
            '/v1/sessions/123/stats',
            {
                'bytes_sent': -20,
                'bytes_received': 40,
                'provider_id': '0x1',
            },
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_sent missing or value is not unsigned int'},
            re.json
        )

        re = self._post(
            '/v1/sessions/123/stats',
            {
                'bytes_sent': 20,
                'bytes_received': -40,
                'provider_id': '0x1',
            },
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_received missing or value is not unsigned int'},
            re.json
        )

        sessions = Session.query.all()
        self.assertEqual(0, len(sessions))

    def test_session_stats_without_provider_id(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'provider_id missing'},
            re.json
        )

        session = Session.query.get('123')
        self.assertIsNone(session)

    def test_session_stats_without_bytes_sent(self):
        payload = {
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_sent missing or value is not unsigned int'},
            re.json
        )

        sessions = Session.query.all()
        self.assertEqual(0, len(sessions))

    def test_session_stats_without_bytes_received(self):
        payload = {
            'bytes_sent': 20,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_received missing or value is not unsigned int'},
            re.json
        )

        sessions = Session.query.all()
        self.assertEqual(0, len(sessions))

    def test_session_stats_when_session_has_expired(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        session = Session('123', 'openvpn')
        session.consumer_id = auth['public_address']
        session.created_at = datetime.utcnow() - timedelta(minutes=11)
        session.client_updated_at = None
        db.session.add(session)
        db.session.commit()
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'session has expired'},
            re.json
        )

        # update client_updated_at in that way session should not expire
        session.client_updated_at = datetime.utcnow() - timedelta(minutes=9)
        db.session.add(session)
        db.session.commit()
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(200, re.status_code)

        # update client_updated_at in that way session should expire
        session.client_updated_at = datetime.utcnow() - timedelta(minutes=11)
        db.session.add(session)
        db.session.commit()
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'session has expired'},
            re.json
        )

    def test_ping_proposal(self):
        payload = {}
        auth = build_test_authorization(json.dumps(payload))

        self._create_node(auth['public_address'], "openvpn")

        re = self._post(
            '/v1/ping_proposal',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)
        pings = NodeAvailability.query.all()
        self.assertEqual(pings[0].service_type, "openvpn")

    def test_ping_proposal_with_service_type(self):
        payload = {'service_type': 'dummy'}
        auth = build_test_authorization(json.dumps(payload))

        self._create_node(auth['public_address'], "dummy")

        re = self._post(
            '/v1/ping_proposal',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        pings = NodeAvailability.query.all()
        self.assertEqual(pings[0].service_type, "dummy")

    def test_ping_proposal_no_node_with_service_type(self):
        payload = {'service_type': 'dummy'}
        auth = build_test_authorization(json.dumps(payload))

        self._create_node(auth['public_address'], "openvpn")

        re = self._post(
            '/v1/ping_proposal',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual({'error': 'node key not found'}, re.json)

    def test_ping_proposal_with_type(self):
        payload = {}
        auth = build_test_authorization(json.dumps(payload))

        node = self._create_node(auth['public_address'], "dummy")

        re = self._post(
            '/v1/ping_proposal',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual({'error': 'node key not found'}, re.json)

        payload = {'service_type': 'dummy'}
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/ping_proposal',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

    def test_node_send_stats_with_unknown_node(self):
        payload = {}
        auth = build_test_authorization(json.dumps(payload))

        re = self._post(
            '/v1/node_send_stats',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual({'error': 'node key not found'}, re.json)

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

    def _create_sample_node(self):
        return self._create_node("node1", "openvpn")

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

    def _create_identity_registration(self, node_key, eth_address):
        ir = IdentityRegistration(node_key, eth_address)
        db.session.add(ir)
        return ir


if __name__ == '__main__':
    unittest.main()
