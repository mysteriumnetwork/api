from dashboard.tests.test_case import TestCase


class TestEndpoints(TestCase):
    def test_main(self):
        re = self._get('/')
        self.assertEqual(200, re.status_code)

    def test_sessions(self):
        re = self._get('/sessions')
        self.assertEqual(200, re.status_code)
