import unittest

import json

from tests.test_case import TestCase


class TestApi(TestCase):
    def test_save_identity(self):
        payload = {
            'identity': '0x0000000000000000000000000000000000000001',
        }

        re = self.client.post('/v1/identities', data=json.dumps(payload))
        self.assertEqual(200, re.status_code)


if __name__ == '__main__':
    unittest.main()
