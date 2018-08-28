import unittest
from tests.test_case import TestCase, main
from tests.utils import generate_test_authorization
from models import Identity


class TestSaveIdentity(TestCase):
    def test_successful(self):
        auth = generate_test_authorization()
        re = self.client.post(
            '/v1/identities',
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        identity_record = Identity.query.get(auth['public_address'])
        self.assertIsNotNone(identity_record)

    def test_failure_identity_already_exists(self):
        auth = generate_test_authorization()

        identity_record = Identity(auth['public_address'])
        main.db.session.add(identity_record)

        re = self.client.post(
            '/v1/identities',
            headers=auth['headers']
        )
        self.assertEqual(403, re.status_code)
        self.assertEqual({"error": 'identity already exists'}, re.json)


if __name__ == '__main__':
    unittest.main()
