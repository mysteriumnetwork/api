import unittest
import json
from tests.test_case import TestCase
from tests.utils import generate_test_authorization


class TestApi(TestCase):
    def test_save_identity(self):
        payload = {
            'identity': '0x0000000000000000000000000000000000000001',
        }

        auth = generate_test_authorization(json.dumps(payload))
        re = self.client.post(
            '/v1/identities',
            data=json.dumps(payload),
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)

    # TODO: test failure scenarios


if __name__ == '__main__':
    unittest.main()
