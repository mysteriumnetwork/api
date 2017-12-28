import unittest

import json

from app import app


class TestApi(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.debug = True
        self.app = app.test_client()

    def test_node_reg(self):

        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": "node1",
            }
        }

        re = self._post('/v1/node_register', payload)

        print re.data
        json.loads(re.data)

    def test_proposals(self):
        re = self.app.get('/v1/proposals')

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertGreater(len(proposals), 0)
        for proposal in proposals:
            self.assertIsNotNone(proposal['id'])

    def test_proposals_filtering(self):
        re = self._get('/v1/proposals', {'node_key': 'node1'})

        self.assertEqual(200, re.status_code)

        data = json.loads(re.data)
        proposals = data['proposals']
        self.assertEqual(1, len(proposals))
        proposal = proposals[0]
        self.assertIsNotNone(proposal['id'])
        self.assertEqual('node1', proposal['provider_id'])

    def test_proposals_with_unknown_node_key(self):
        re = self._get('/v1/proposals', {'node_key': 'UNKNOWN'})

        self.assertEqual(200, re.status_code)
        data = json.loads(re.data)
        self.assertEqual([], data['proposals'])

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

        print re.data
        data = json.loads(re.data)
        for el in data['sessions']:
            el['is_session_valid']
            el['session_key']

    # TODO: fix test
    def _test_client_send_stats(self):
        payload = {
            'session_key': 'X2d9gyQk1j',
            'bytes_sent': 50,
            'bytes_received': 60,
        }

        re = self._post('/v1/client_send_stats', payload)

        print re.data
        data = json.loads(re.data)
        data['is_session_valid']
        data['session_key']

    def _get(self, url, params={}):
        return self.app.get(url, query_string=params)

    def _post(self, url, payload):
        return self.app.post(url, data=json.dumps(payload))


if __name__ == '__main__':
    unittest.main()
