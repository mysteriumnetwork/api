from tests.test_case import TestCase
from eth_keys import keys
import json
import base64

class TestApi(TestCase):
    def sign_message(self, message):
        pk = keys.PrivateKey(b'\x01' * 32)
        signature = pk.sign_msg(message)
        signature_bytes =signature.to_bytes()
        public_address = pk.public_key.to_checksum_address()
        return signature_bytes, public_address

    def test_incorrect_authorization_header(self):
        headers = {
            "incorrectAuthorizationHeader": "Signature sig"
        }

        re = self.client.post(
            '/v1/test_signed_payload',
            data=json.dumps(''),
            headers=headers
        )

        self.assertEqual(401, re.status_code)
        self.assertEqual(re.json['error'], 'missing Authorization in request header')

    def test_incorrect_authorization_header_value_format(self):
        headers = {
            "Authorization": "Signature"
        }

        re = self.client.post(
            '/v1/test_signed_payload',
            data=json.dumps(''),
            headers=headers
        )

        self.assertEqual(401, re.status_code)
        self.assertEqual(re.json['error'], 'invalid Authorization header value provided, correct format: Signature <signature_base64_encoded>')

    def test_incorrect_authorization_type(self):
        headers = {
            "Authorization": "incorrectType sig"
        }

        re = self.client.post(
            '/v1/test_signed_payload',
            data=json.dumps(''),
            headers=headers
        )

        self.assertEqual(401, re.status_code)
        self.assertEqual(re.json['error'], 'authentication type have to be Signature')

    def test_empty_authorization_header_value(self):
        headers = {
            "Authorization": "Signature "
        }

        re = self.client.post(
            '/v1/test_signed_payload',
            data=json.dumps(''),
            headers=headers
        )

        self.assertEqual(401, re.status_code)
        self.assertEqual(re.json['error'], 'signature was not provided')

    def test_signature_not_base64_encoded(self):
        headers = {
            "Authorization": "Signature not_base_64"
        }

        re = self.client.post(
            '/v1/test_signed_payload',
            data=json.dumps(''),
            headers=headers
        )

        self.assertEqual(401, re.status_code)
        self.assertEqual(re.json['error'], 'signature must be base64 encoded: Incorrect padding')

    def test_incorrect_signature_format(self):
        payload = {
            "test": "test"
        }

        signature, public_address = self.sign_message(json.dumps(payload))

        headers = {
            "Authorization": "Signature {}".format(base64.b64encode(signature+'1'))
        }

        re = self.client.post(
            '/v1/test_signed_payload',
            data=json.dumps(payload),
            headers=headers
        )

        self.assertEqual(401, re.status_code)
        self.assertEqual(re.json['error'], 'invalid signature format: Unexpected signature format.  Must be length 65 byte string')

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