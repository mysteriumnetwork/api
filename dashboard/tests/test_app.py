from dashboard.tests.test_case import TestCase


class TestEndpoints(TestCase):
    def test_sessions(self):
        re = self._get('/sessions')
        self.assertEqual(200, re.status_code)

    def _get(self, url, params={}):
        return self.client.get(
            url,
            query_string=params,
        )
