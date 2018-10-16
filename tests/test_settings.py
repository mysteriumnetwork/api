import unittest
from unittest import mock
import os
import importlib


class TestSettings(unittest.TestCase):
    @mock.patch.dict(os.environ, {})
    def test_default_values(self):
        import settings
        importlib.reload(settings)
        self.assertEqual(80, settings.APP_PORT)
        self.assertEqual('localhost', settings.DB_HOST)
        self.assertEqual('', settings.DB_NAME)
        self.assertEqual('', settings.USER)
        self.assertEqual('', settings.PASSWD)
        self.assertEqual(False, settings.RESTRICT_BY_IP_ENABLED)
        self.assertEqual([''], settings.ALLOWED_IP_ADDRESSES)
        self.assertEqual('https://ropsten.infura.io/', settings.ETHER_RPC_URL)
        self.assertEqual('pow', settings.ETHER_MINING_MODE)
        self.assertEqual(
            '0xbe5F9CCea12Df756bF4a5Baf4c29A10c3ee7C83B',
            settings.IDENTITY_CONTRACT
        )

    @mock.patch.dict(os.environ, {'ETHER_MINING_MODE': 'pow'})
    def test_mining_mode_pow(self):
        import settings
        importlib.reload(settings)
        self.assertEqual('pow', settings.ETHER_MINING_MODE)

    @mock.patch.dict(os.environ, {'ETHER_MINING_MODE': 'poa'})
    def test_mining_mode_poa(self):
        import settings
        importlib.reload(settings)
        self.assertEqual('poa', settings.ETHER_MINING_MODE)

    @mock.patch.dict(os.environ, {'ETHER_MINING_MODE': 'some'})
    def test_mining_mode_handles_unsupported_exception(self):

        with self.assertRaises(Exception) as err:
            import settings
            importlib.reload(settings)
        self.assertEqual(
            'Not supported ether mining mode',
            str(err.exception)
        )

    @mock.patch.dict(os.environ, {'DISCOVERY_VERIFY_IDENTITY': 'true'})
    def test_is_identity_verification_enabled(self):
        import settings
        importlib.reload(settings)
        self.assertEqual(True, settings.DISCOVERY_VERIFY_IDENTITY)

    @mock.patch.dict(os.environ, {'DISCOVERY_VERIFY_IDENTITY': 'false'})
    def test_is_identity_verification_disabled(self):
        import settings
        importlib.reload(settings)
        self.assertEqual(False, settings.DISCOVERY_VERIFY_IDENTITY)

    def test_is_identity_verification_disabled(self):
        import settings
        importlib.reload(settings)
        self.assertEqual(True, settings.DISCOVERY_VERIFY_IDENTITY)


if __name__ == '__main__':
    unittest.main()
