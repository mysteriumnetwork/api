import unittest
import json
from tests.test_case import TestCase
from tests.utils import generate_test_authorization
from models import Identity


class TestSaveIdentity(TestCase):
    def test_successful(self):
        payload = json.dumps({})
        auth = generate_test_authorization(payload)
        re = self.client.post(
            '/v1/identities',
            data=payload,
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)

        identity_record = Identity.query.get(auth['public_address'])
        self.assertIsNotNone(identity_record)

    # TODO: test failure scenarios


if __name__ == '__main__':
    unittest.main()
