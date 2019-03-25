from tests.test_case import TestCase
from tests.utils import build_test_authorization


class TestApi(TestCase):
    def test_successful_request(self):
        auth = build_test_authorization()
        re = self.client.get('/v1/me', headers=auth['headers'])

        self.assertEqual(200, re.status_code)
        self.assertEqual(
            re.json,
            {'identity': auth['public_address']}
        )

    def test_failure(self):
        re = self.client.get(
            '/v1/me',
            headers={"Authorization": ""}
        )

        self.assertEqual(401, re.status_code)
        self.assertEqual(
            re.json,
            {'error': 'missing Authorization in request header'}
        )
