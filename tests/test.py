import unittest

import json

from models import Session, Node
from tests.test_case import TestCase, db
import helpers
import base64


class TestApi(TestCase):
    def test_node_reg(self):
        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": "node1",
            }
        }

        re = self._post('/v1/node_register', payload)
        self.assertEqual(200, re.status_code)

        re.json

    def test_node_reg_with_invalid_json(self):
        re = self.client.post('/v1/node_register', data='{asd}')
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'payload must be a valid json'}, re.json)

    def test_node_reg_with_string_json(self):
        # string is actually a valid json,
        # but endpoints rely on json being a dictionary
        re = self.client.post('/v1/node_register', data='"some string"')
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'payload must be a valid json'}, re.json)

    def test_node_reg_with_array_json(self):
        # string is actually a valid json,
        # but endpoints rely on json being a dictionary
        re = self.client.post('/v1/node_register', data='[]')
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
        signature, public_address = helpers.sign_message_with_static_key('')
        headers = {
            "Authorization": "Signature {}".format(base64.b64encode(signature))
        }
        re = self._post(
            '/v1/sessions/123/stats',
            {
                'bytes_sent': 20,
                'bytes_received': 40
            },
            headers=headers
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        sessions = Session.query.all()
        self.assertEqual(1, len(sessions))
        session = sessions[0]
        self.assertEqual('123', session.session_key)
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertEqual('127.0.0.1', session.client_ip)

    def test_session_stats_create_with_session_record(self):
        session = Session('123')
        db.session.add(session)
        db.session.commit()

        signature, public_address = helpers.sign_message_with_static_key('')
        headers = {
            "Authorization": "Signature {}".format(base64.b64encode(signature))
        }
        re = self._post(
            '/v1/sessions/123/stats',
            {
                'bytes_sent': 20,
                'bytes_received': 40,
            },
            headers=headers
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        sessions = Session.query.all()
        self.assertEqual(1, len(sessions))
        session = sessions[0]
        self.assertEqual('123', session.session_key)
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)

    def test_session_stats_create_with_negative_values(self):
        signature, public_address = helpers.sign_message_with_static_key('')
        headers = {
            "Authorization": "Signature {}".format(base64.b64encode(signature))
        }
        re = self._post(
            '/v1/sessions/123/stats',
            {
                'bytes_sent': -20,
                'bytes_received': 40
            },
            headers=headers
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_sent should not be negative'},
            re.json
        )

        re = self._post(
            '/v1/sessions/123/stats',
            {
                'bytes_sent': 20,
                'bytes_received': -40
            },
            headers=headers
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_received should not be negative'},
            re.json
        )

        sessions = Session.query.all()
        self.assertEqual(0, len(sessions))

    # TODO: fix test
    def _test_node_send_stats(self):
        session = {
            'session_key': 'X2d9gyQk1j',
            'bytes_sent': 20,
            'bytes_received': 10,
        }

        payload = {
            'node_key': 'node key',
            'sessions': [session]
        }

        re = self._post('/v1/node_send_stats', payload)

        data = json.loads(re.data)
        for el in data['sessions']:
            el['is_session_valid']
            el['session_key']

    def _get(self, url, params={}):
        return self.client.get(url, query_string=params)

    def _post(self, url, payload, headers=None):
        return self.client.post(url, data=json.dumps(payload), headers=headers)

    def _create_sample_node(self):
        node = Node("node1")
        node.proposal = json.dumps({
            "id": 1,
            "format": "service-proposal/v1",
            "provider_id": "node1",
        })
        db.session.add(node)


if __name__ == '__main__':
    unittest.main()
