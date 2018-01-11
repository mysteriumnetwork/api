import unittest
import json
from tests.test_case import TestCase
import base64
import helpers


class TestApi(TestCase):
    def test_save_identity(self):
        payload = {
            'identity': '0x0000000000000000000000000000000000000001',
        }

        signature, public_address = helpers.sign_message_with_static_key(
            json.dumps(payload)
        )

        headers = {
            "Authorization": "Signature {}".format(base64.b64encode(signature))
        }

        re = self.client.post(
            '/v1/identities',
            data=json.dumps(payload),
            headers=headers
        )
        self.assertEqual(200, re.status_code)

    # TODO: test failure scenarios


if __name__ == '__main__':
    unittest.main()
