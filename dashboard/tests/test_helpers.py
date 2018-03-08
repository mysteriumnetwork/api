import unittest
from dashboard.helpers import shorten_node_key, get_natural_size


class TestHelpers(unittest.TestCase):
    def test_shorten_node_key_success(self):
        self.assertEqual(
            '0x1234..abcd',
            shorten_node_key('0x123400000000000000000000000000000000abcd')
        )

    def test_shorten_node_key_incorrect_length(self):
        self.assertEqual(
            '0x',
            shorten_node_key('0x')
        )

    def test_shorten_node_key_none(self):
        self.assertEqual(
            None,
            shorten_node_key(None)
        )

    def test_get_natural_size_1byte(self):
        self.assertEqual(
            '1 Byte',
            get_natural_size(1)
        )

    def test_get_natural_size_1kb(self):
        self.assertEqual(
            '1.00 KB',
            get_natural_size(1024)
        )

    def test_get_natural_size_1mb(self):
        self.assertEqual(
            '1.00 MB',
            get_natural_size(1024 * 1024)
        )

    def test_get_natural_size_1gb(self):
        self.assertEqual(
            '1.00 GB',
            get_natural_size(1024 * 1024 * 1024)
        )
