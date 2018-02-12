from tests.test_case import TestCase
from ip import detect_country


class TestApi(TestCase):
    def test_detect_country(self):
        self.assertEqual('US', detect_country('8.8.8.8'))
        self.assertRaises(ValueError, detect_country, 'not an ip')
        self.assertEqual(None, detect_country('127.0.0.1'))
