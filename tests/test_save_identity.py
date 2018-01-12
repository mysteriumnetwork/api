import unittest
import json
from tests.test_case import TestCase, db
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
        self.assertEqual({}, re.json)

        identity_record = Identity.query.get(auth['public_address'])
        self.assertIsNotNone(identity_record)

    def test_failure_identity_already_exists(self):
        payload = json.dumps({})
        auth = generate_test_authorization(payload)

        identity_record = Identity(auth['public_address'])
        db.session.add(identity_record)

        re = self.client.post(
            '/v1/identities',
            data=payload,
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual({"error": 'identity already exists'}, re.json)


if __name__ == '__main__':
    unittest.main()
