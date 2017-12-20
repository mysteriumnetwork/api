import unittest

import requests
import json


class TestApi(unittest.TestCase):
    def test_node_reg(self):

        payload = {
            "service_proposal": {
                "id": 1,
                "format": "service-proposal/v1",
                "provider_id": "node1",
            }
        }

        re = requests.post(
            'http://127.0.0.1:5000/v1/node_register',
            data=json.dumps(payload)
        )

        print re.content
        re.json()

    def test_client_create_session(self):
        payload = {
            'node_key': 'node1',
        }

        re = requests.post(
            'http://127.0.0.1:5000/v1/client_create_session',
            data=json.dumps(payload)
        )
        print re.content
        data = re.json()
        data['session_key']
        data['service_proposal']

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

        re = requests.post(
            'http://127.0.0.1:5000/v1/node_send_stats',
            data = json.dumps(payload)
        )

        print re.content
        data = re.json()
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

        re = requests.post(
            'http://127.0.0.1:5000/v1/client_send_stats',
            data = json.dumps(payload)
        )

        print re.content
        data = re.json()
        data['is_session_valid']
        data['session_key']


if __name__ == '__main__':
    unittest.main()
