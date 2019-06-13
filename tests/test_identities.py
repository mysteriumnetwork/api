from tests.test_case import TestCase
from tests.utils import (
    build_test_authorization,
    build_static_public_address
)
from models import IdentityRegistration
import json
from models import db


class TestIdentities(TestCase):
    def test_payout_no_payout_address(self):
        identity = build_static_public_address().upper()
        payload = {}
        auth = build_test_authorization(json.dumps(payload))
        re = self._put(
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
        auth = build_test_authorization(json.dumps(payload))
        re = self._put(
            '/v1/identities/mismatch/payout',
            payload,
            headers=auth['headers']
        )
        msg = 'no permission to modify this identity'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(403, re.status_code)

    def test_payout_incorrect_eth_address(self):
        identity = build_static_public_address().upper()
        payload = {
            'payout_eth_address': 'any'
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._put(
            '/v1/identities/{}/payout'.format(identity),
            payload,
            headers=auth['headers']
        )
        msg = 'payout_eth_address is not in Ethereum address format'
        self.assertEqual({'error': msg}, re.json)
        self.assertEqual(400, re.status_code)

    def test_payout_create(self):
        identity = build_static_public_address().upper()
        payload = {
            'payout_eth_address': '0x000000000000000000000000000000000000000a'
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._put(
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
        identity = build_static_public_address().upper()
        pre_record = IdentityRegistration(identity.lower(), '')
        db.session.add(pre_record)
        db.session.commit()

        payload = {
            'payout_eth_address': '0x000000000000000000000000000000000000000a'
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._put(
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

    def test_referral_code_update(self):
        identity = build_static_public_address().upper()
        pre_record = IdentityRegistration(identity.lower(), '')
        db.session.add(pre_record)
        db.session.commit()

        payload = {
            'payout_eth_address': '0x000000000000000000000000000000000000000a',
            'referral_code': 'ABC123'
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._put(
            '/v1/identities/{}/payout'.format(identity),
            payload,
            headers=auth['headers']
        )
        self.assertEqual({}, re.json)
        self.assertEqual(200, re.status_code)

        # test updated values
        record = IdentityRegistration.query.get(identity.lower())
        self.assertEqual(
            'ABC123',
            record.referral_code
        )
        self.assertIsNotNone(record.updated_at)

    def test_get_payout_returns_eth_address(self):
        identity = build_static_public_address().upper()
        eth_address = build_static_public_address().upper()
        pre_record = IdentityRegistration(identity.lower(), eth_address)
        db.session.add(pre_record)
        db.session.commit()

        auth = build_test_authorization()
        re = self._get(
            '/v1/identities/{}/payout'.format(identity),
            headers=auth['headers']
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({'eth_address': eth_address}, re.json)

    def test_get_payout_returns_404_with_no_payout_info(self):
        identity = build_static_public_address().upper()

        auth = build_test_authorization()
        re = self._get(
            '/v1/identities/{}/payout'.format(identity),
            headers=auth['headers']
        )
        self.assertEqual(404, re.status_code)
        self.assertEqual(
            {'error': 'payout info for this identity not found'},
            re.json)

    def test_get_payout_returns_403_when_requesting_other_identity(self):
        other_identity = '0X000000000000000000000000000000000000000A'
        eth_address = build_static_public_address().upper()
        pre_record = IdentityRegistration(other_identity.lower(), eth_address)
        db.session.add(pre_record)
        db.session.commit()

        auth = build_test_authorization()
        re = self._get(
            '/v1/identities/{}/payout'.format(other_identity),
            headers=auth['headers']
        )
        self.assertEqual(403, re.status_code)
        self.assertEqual(
            {'error': 'no permission to access this identity'},
            re.json)
