from tests.test_case import TestCase
import base64
from tests.utils import sign_message_with_static_key


class TestApi(TestCase):
    def test_successful_request(self):
        signature, public_address = sign_message_with_static_key('')
        headers = {
            "Authorization": "Signature {}".format(base64.b64encode(signature))
        }

        re = self.client.get('/v1/me', headers=headers)

        self.assertEqual(200, re.status_code)
        self.assertEqual(
            re.json,
            {'identity': public_address.lower()}
        )

    def test_failure(self):
        re = self.client.get(
            '/v1/me',
            headers={"Authorization": ""}
        )

        self.assertEqual(401, re.status_code)
        self.assertEqual(
            re.json,
            {'error': 'missing Authorization in request header'}
        )
