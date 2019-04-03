from dashboard.tests.test_case import TestCase


class TestEndpoints(TestCase):
    def test_main(self):
        re = self._get('/')
        self.assertEqual(200, re.status_code)

    def test_sessions(self):
        re = self._get('/sessions')
        self.assertEqual(200, re.status_code)

    def test_leaderboard(self):
        re = self._get('/leaderboard')
        self.assertEqual(200, re.status_code)

    def test_leaderboard_get_page(self):
        re = self._get('/leaderboard', {'page': 1})
        self.assertEqual(200, re.status_code)

    def test_leaderboard_handle_invalid_int_as_page_number(self):
        re = self._get('/leaderboard', {'page': 'a'})
        self.assertEqual(400, re.status_code)

    def test_leaderboard_handle_invalid_page_number(self):
        re = self._get('/leaderboard', {'page': 0})
        self.assertEqual(400, re.status_code)
