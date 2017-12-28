import unittest

import json

from app import app, db


class TestApi(unittest.TestCase):
    def setUp(self):
        app.testing = True
        app.debug = True
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_save_identity(self):
        payload = {
            'identity': '0x0000000000000000000000000000000000000001',
        }

        re = self.app.post('/v1/identities', data=json.dumps(payload))
        print re.data
        self.assertEqual(200, re.status_code)


if __name__ == '__main__':
    unittest.main()
