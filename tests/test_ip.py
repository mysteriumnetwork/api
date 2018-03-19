from tests.test_case import TestCase
from ip import mask_ip_partially


class TestApi(TestCase):
    def test_mask_ip_partially(self):
        self.assertEqual('1.2.3.X', mask_ip_partially('1.2.3.4'))
        self.assertRaises(ValueError, mask_ip_partially, '1.2.3.4.5')
        self.assertRaises(ValueError, mask_ip_partially, 'abc')
