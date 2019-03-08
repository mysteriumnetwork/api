from tests.test_case import TestCase, main
from tests.utils import (
    generate_test_authorization,
    generate_static_public_address
)
from models import IdentityRegistration
import json


class TestPost(TestCase):
    def test_payout_no_payout_address(self):
        identity = generate_static_public_address().upper()
        payload = {}
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/{}/payout'.format(identity),
            payload,
            headers=auth['headers']
        )
        msg = 'missing payout_eth_address parameter in body'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(400, re.status_code)

    def test_payout_url_parameter_mismatch(self):
        payload = {
            'payout_eth_address': '0x'
        }
        auth = generate_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/identities/mismatch/payout',
            payload,
            headers=auth['headers']
        )
        msg = 'no permission to modify this identity'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(403, re.status_code)

    def test_payout_incorrect_eth_address(self):
        identity = generate_static_public_address().upper()
        payload = {
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

    def test_payout_create(self):
        identity = generate_static_public_address().upper()
        payload = {
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

        # test inserted values
        record = IdentityRegistration.query.get(identity.lower())
        self.assertEqual(
            '0x000000000000000000000000000000000000000a',
            record.payout_eth_address
        )
        self.assertIsNotNone(record.created_at)
        self.assertIsNone(record.updated_at)

    def test_payout_update(self):
        identity = generate_static_public_address().upper()
        pre_record = IdentityRegistration(identity.lower(), '')
        main.db.session.add(pre_record)
        main.db.session.commit()

        payload = {
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

        # test updated values
        record = IdentityRegistration.query.get(identity.lower())
        self.assertEqual(
            '0x000000000000000000000000000000000000000a',
            record.payout_eth_address
        )
        self.assertIsNotNone(record.updated_at)
