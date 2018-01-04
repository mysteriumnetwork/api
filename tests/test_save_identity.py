import unittest

import json

from tests.test_case import TestCase


class TestApi(TestCase):
    def test_save_identity(self):
        payload = {}

        headers = {
            "Authorization": "Signature Da1mAwK5abmXQCNsCE+YjsZbR9jTyEKqdrjxxMKwNzwr2NFnM35UiVQJWcg8rgL+X2PR60LoIUMlGU9OPaSoZwE="
        }

        re = self.client.post('/v1/identities', headers=headers, data=json.dumps(payload))
        self.assertEqual(200, re.status_code)


if __name__ == '__main__':
    unittest.main()
