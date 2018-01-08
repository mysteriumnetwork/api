from tests.test_case import TestCase
from eth_keys import keys
import base64

class TestApi(TestCase):
    def sign_message(self, message):
        pk = keys.PrivateKey(b'\x01' * 32)
        signature = pk.sign_msg(message)
        signature_bytes =signature.to_bytes()
        public_address = pk.public_key.to_checksum_address()
        return signature_bytes, public_address

    def test_successful_request(self):
        signature, public_address = self.sign_message('')

        headers = {
            "Authorization": "Signature {}".format(base64.b64encode(signature))
        }

        re = self.client.post(
            '/v1/test_signed_payload',
            headers=headers
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual(public_address.lower(), re.json['identity'])

    def test_failure(self):
        headers = {
            "Authorization": ""
        }

        re = self.client.post(
            '/v1/test_signed_payload',
            headers=headers
        )

        self.assertEqual(401, re.status_code)