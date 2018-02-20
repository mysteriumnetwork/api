import unittest
import json
from models import Session, Node
from tests.test_case import TestCase, db
from tests.utils import (
    generate_test_authorization,
    generate_static_public_address,
)
import settings


class TestApi(TestCase):
    REMOTE_ADDR = '8.8.8.8'

    def test_register_proposal_successful(self):
        settings.RESTRICT_BY_IP_ENABLED = False
        public_address = generate_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
            }
        }

        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'])
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        node = Node.query.get(public_address)
        self.assertEqual(self.REMOTE_ADDR, node.ip)
        self.assertEqual('US', node.country)

    def test_register_proposal_with_unknown_ip(self):
        settings.RESTRICT_BY_IP_ENABLED = False
        public_address = generate_static_public_address()
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": public_address,
            }
        }

        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/register_proposal',
            payload,
            headers=auth['headers'],
            remote_addr='127.0.0.1'
        )
        self.assertEqual(200, re.status_code)
        self.assertIsNotNone(re.json)

        node = Node.query.get(public_address)
        self.assertEqual('127.0.0.1', node.ip)
        self.assertEqual('', node.country)

    def test_register_proposal_unauthorized(self):
        settings.RESTRICT_BY_IP_ENABLED = False
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": "incorrect",
            }
        }

        auth = generate_test_authorization(json.dumps(payload))
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

    def test_register_proposal_with_invalid_json(self):
        settings.RESTRICT_BY_IP_ENABLED = False
        re = self.client.post('/v1/register_proposal', data='{asd}')
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'payload must be a valid json'}, re.json)

    def test_register_proposal_with_string_json(self):
        settings.RESTRICT_BY_IP_ENABLED = False
        # string is actually a valid json,
        # but endpoints rely on json being a dictionary
        re = self.client.post('/v1/register_proposal', data='"some string"')
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'payload must be a valid json'}, re.json)

    def test_register_proposal_with_array_json(self):
        settings.RESTRICT_BY_IP_ENABLED = False
        # string is actually a valid json,
        # but endpoints rely on json being a dictionary
        re = self.client.post('/v1/register_proposal', data='[]')
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'payload must be a valid json'}, re.json)

    def test_proposals(self):
        self._create_sample_node()

        re = self._get('/v1/proposals')

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertGreater(len(proposals), 0)
        for proposal in proposals:
            self.assertIsNotNone(proposal['id'])

    def test_proposals_filtering(self):
        self._create_sample_node()

        re = self._get('/v1/proposals', {'node_key': 'node1'})

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertEqual(1, len(proposals))
        proposal = proposals[0]
        self.assertIsNotNone(proposal['id'])
        self.assertEqual('node1', proposal['provider_id'])

    def test_proposals_with_unknown_node_key(self):
        self._create_sample_node()

        re = self._get('/v1/proposals', {'node_key': 'UNKNOWN'})

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual([], data['proposals'])

    def test_session_stats_create_without_session_record(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = generate_test_authorization(json.dumps(payload))
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
        self.assertEqual('US', session.client_country)
        self.assertEqual('0x1', session.node_key)

    def test_session_stats_create_without_session_record_with_unknown_ip(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = generate_test_authorization(json.dumps(payload))
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
        auth = generate_test_authorization(json.dumps(payload))

        session = Session('123')
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
        session = Session('123')
        session.consumer_id = 'different'
        db.session.add(session)
        db.session.commit()

        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = generate_test_authorization(json.dumps(payload))
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
        auth = generate_test_authorization()
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
        auth = generate_test_authorization(json.dumps(payload))
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
        auth = generate_test_authorization(json.dumps(payload))
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
        auth = generate_test_authorization(json.dumps(payload))
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

    def test_ping_proposal(self):
        settings.RESTRICT_BY_IP_ENABLED = False
        payload = {}
        auth = generate_test_authorization(json.dumps(payload))

        self._create_node(auth['public_address'])

        re = self._post(
            '/v1/ping_proposal',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

    def test_node_send_stats_with_unknown_node(self):
        settings.RESTRICT_BY_IP_ENABLED = False
        payload = {}
        auth = generate_test_authorization(json.dumps(payload))

        re = self._post(
            '/v1/node_send_stats',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual({'error': 'node key not found'}, re.json)

    def test_restrict_by_ip_fail(self):
        settings.RESTRICT_BY_IP_ENABLED = True
        settings.ALLOWED_IP_ADDRESSES = [
            '1.1.1.1',
            '2.2.2.2',
        ]
        payload = {}
        auth = generate_test_authorization(json.dumps(payload))

        self._create_node(auth['public_address'])

        re = self._post(
            '/v1/ping_proposal',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(403, re.status_code)
        self.assertEqual({'error': 'resource is forbidden'}, re.json)

    def test_restrict_by_ip_success(self):
        settings.RESTRICT_BY_IP_ENABLED = True
        settings.ALLOWED_IP_ADDRESSES = [
            '1.1.1.1',
            '2.2.2.2',
            self.REMOTE_ADDR
        ]
        payload = {}
        auth = generate_test_authorization(json.dumps(payload))

        self._create_node(auth['public_address'])

        re = self._post(
            '/v1/ping_proposal',
            payload,
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

    def _get(self, url, params={}):
        return self.client.get(
            url,
            query_string=params,
            environ_base={'REMOTE_ADDR': self.REMOTE_ADDR}
        )

    def _post(self, url, payload, headers=None, remote_addr=None):
        return self.client.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            environ_base={'REMOTE_ADDR': remote_addr or self.REMOTE_ADDR}
        )

    def _create_sample_node(self):
        self._create_node("node1")

    def _create_node(self, node_key):
        node = Node(node_key)
        node.proposal = json.dumps({
            "id": 1,
            "format": "service-proposal/v1",
            "provider_id": node_key,
        })
        db.session.add(node)


if __name__ == '__main__':
    unittest.main()
