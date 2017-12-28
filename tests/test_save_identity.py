import unittest

import json

from app import app


class TestApi(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.debug = True
        self.app = app.test_client()

    # TODO: assert response, fix it to be 200
    def test_save_identity(self):
        payload = {
            'identity': '0x0000000000000000000000000000000000000001',
        }

        re = self.app.post('/v1/identities', data=json.dumps(payload))
        print re.data


if __name__ == '__main__':
    unittest.main()
