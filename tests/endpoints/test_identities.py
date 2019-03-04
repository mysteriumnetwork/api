from tests.test_case import TestCase, main
from tests.utils import (
    generate_test_authorization,
    generate_static_public_address,
    sign_message_with_static_key
)
from models import IdentityRegistration
import json
import base64


class TestPost(TestCase):
    def test_identity_payout_no_provider_id(self):
        identity = generate_static_public_address().upper()
        payload = {
            'payout_eth_address': ''
        }
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/{}/payout'.format(identity),
            payload,
            headers=auth['headers']
        )
        msg = 'missing identity parameter in body'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(400, re.status_code)

    def test_identity_payout_no_payout_address(self):
        identity = generate_static_public_address().upper()
        payload = {
            'identity': ''
        }
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/{}/payout'.format(identity),
            payload,
            headers=auth['headers']
        )
        msg = 'missing payout_eth_address parameter in body'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(400, re.status_code)

    def test_identity_payout_url_parameter_mismatch(self):
        identity = generate_static_public_address().upper()
        payload = {
            'identity': identity,
            'payout_eth_address': '0x000000000000000000000000000000000000000a'
        }
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/mismatch/payout',
            payload,
            headers=auth['headers']
        )
        msg = 'identity parameter in url does not match with provider_id'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(400, re.status_code)

    def test_identity_payout_address_mismatch_signer_identity(self):
        payload = {
            'identity': 'different_identity',
            'payout_eth_address': '0x000000000000000000000000000000000000000a'
        }
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/different_identity/payout',
            payload,
            headers=auth['headers']
        )
        msg = 'identity parameter in body does not match with signer identity'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(400, re.status_code)

    def test_identity_payout_incorrect_eth_address(self):
        identity = generate_static_public_address().upper()
        payload = {
            'identity': identity,
            'payout_eth_address': 'any'
        }
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/{}/payout'.format(identity),
            payload,
            headers=auth['headers']
        )
        msg = 'payout_eth_address is not in Ethereum address format'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(400, re.status_code)

    def test_identity_payout_identity_already_exists(self):
        identity = generate_static_public_address().upper()
        model = IdentityRegistration(identity.lower(), '', '', '')
        main.db.session.add(model)
        main.db.session.commit()

        payload = {
            'identity': identity,
            'payout_eth_address': '0x000000000000000000000000000000000000000a'
        }
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/{}/payout'.format(identity),
            payload,
            headers=auth['headers']
        )
        msg = 'identity payout address already registered'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(403, re.status_code)

    def test_identity_payout_address(self):
        identity = generate_static_public_address().upper()
        payload = {
            'identity': identity,
            'payout_eth_address': '0x000000000000000000000000000000000000000a'
        }
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/{}/payout'.format(identity),
            payload,
            headers=auth['headers']
        )
        self.assertEqual({}, re.json)
        self.assertEqual(200, re.status_code)

        # test stored payout_eth_address
        record = IdentityRegistration.query.get(identity.lower())
        self.assertEqual(
            '0x000000000000000000000000000000000000000a',
            record.payout_eth_address
        )

        # test stored signature
        self.assertEqual(
            sign_message_with_static_key(json.dumps(payload)),
            base64.b64decode(record.signature)
        )

        # test stored signed_body
        self.assertEqual(
            json.dumps(payload),
            base64.b64decode(record.signed_body).decode('utf-8')
        )
