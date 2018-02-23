import unittest
from dashboard.helpers import shorten_node_key

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
