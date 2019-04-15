import unittest
from datetime import timedelta, datetime, date
from dashboard.helpers import (
    shorten_node_key,
    format_bytes_count,
    format_duration,
    get_week_range
)


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

    def test_format_bytes_count(self):
        self.assertEqual(
            '1 Byte',
            format_bytes_count(1)
        )

        self.assertEqual(
            '1.00 KB',
            format_bytes_count(1024)
        )

        self.assertEqual(
            '1.00 MB',
            format_bytes_count(1024 * 1024)
        )

        self.assertEqual(
            '1.00 GB',
            format_bytes_count(1024 * 1024 * 1024)
        )

    def test_format_duration(self):
        self.assertEqual(
            '< 1 minute',
            format_duration(timedelta(seconds=0))
        )

        self.assertEqual(
            '< 1 minute',
            format_duration(timedelta(seconds=59))
        )

        self.assertEqual(
            '1min',
            format_duration(timedelta(seconds=60))
        )

        self.assertEqual(
            '1hr 0min',
            format_duration(timedelta(minutes=60))
        )

        self.assertEqual(
            '100hr 1min',
            format_duration(timedelta(hours=100, minutes=1))
        )

    def test_get_week_range(self):
        fixed_date = date(2019, 3, 20)
        date_from, date_to = get_week_range(fixed_date)
        self.assertEqual(datetime(2019, 3, 18, 0, 0, 0), date_from)
        self.assertEqual(datetime(2019, 3, 25, 0, 0, 0), date_to)
