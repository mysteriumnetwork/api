import unittest
from tests.test_case import TestCase
from app import decode_authorization_header
from eth_keys import keys
import base64


class TestAuthorizationHeader(TestCase):
    def sign_message(self, message):
        pk = keys.PrivateKey(b'\x01' * 32)
        signature = pk.sign_msg(message)
        signature_bytes = signature.to_bytes()
        public_address = pk.public_key.to_checksum_address()
        return signature_bytes, public_address

    def test_incorrect_authorization_header(self):
        headers = {
            "incorrectAuthorizationHeader": "Signature sig"
        }

        with self.assertRaises(ValueError) as err:
            decode_authorization_header(headers)
        self.assertEqual(
            'missing Authorization in request header',
            str(err.exception)
        )

    def test_incorrect_authorization_header_value_format(self):
        headers = {
            "Authorization": "Signature"
        }

        with self.assertRaises(ValueError) as err:
            decode_authorization_header(headers)
        self.assertEqual(
            'invalid Authorization header value provided, correct'
            ' format: Signature <signature_base64_encoded>',
            str(err.exception)
        )

    def test_incorrect_authorization_type(self):
        headers = {
            "Authorization": "incorrectType sig"
        }

        with self.assertRaises(ValueError) as err:
            decode_authorization_header(headers)
        self.assertEqual(
            'authentication type have to be Signature',
            str(err.exception)
        )

    def test_empty_authorization_header_value(self):
        headers = {
            "Authorization": "Signature "
        }

        with self.assertRaises(ValueError) as err:
            decode_authorization_header(headers)
        self.assertEqual('signature was not provided', str(err.exception))

    def test_signature_not_base64_encoded(self):
        headers = {
            "Authorization": "Signature not_base_64"
        }

        with self.assertRaises(ValueError) as err:
            decode_authorization_header(headers)
        self.assertEqual(
            'signature must be base64 encoded: Incorrect padding',
            str(err.exception)
        )

    def test_incorrect_signature_format(self):
        signature, public_address = self.sign_message('')
        invalid_signature = base64.b64encode(signature+'1')

        headers = {
            "Authorization": "Signature {}".format(invalid_signature)
        }

        with self.assertRaises(ValueError) as err:
            decode_authorization_header(headers)
        self.assertEqual(
            'invalid signature format: Unexpected signature format.'
            '  Must be length 65 byte string',
            str(err.exception)
        )

    def test_successful(self):
        signature, public_address = self.sign_message('')

        headers = {
            "Authorization": "Signature {}".format(base64.b64encode(signature))
        }

        recovered_public_address = decode_authorization_header(headers)
        self.assertEqual(public_address.lower(), recovered_public_address)


if __name__ == '__main__':
    unittest.main()
