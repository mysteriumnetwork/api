import unittest

import requests
import json


class TestApi(unittest.TestCase):
    def test_save_identity(self):
        payload = {
            'identity': '0x0000000000000000000000000000000000000001',
        }

        re = requests.post(
            'http://127.0.0.1:5000/v1/identities',
            data=json.dumps(payload)
        )
        print re.content


if __name__ == '__main__':
    unittest.main()
