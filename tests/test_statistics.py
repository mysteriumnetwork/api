from datetime import datetime

from tests.test_case import TestCase
from models import db, Session


class TestStatistics(TestCase):
    def test_sessions_returns_sessions(self):
        self._create_session('test-session')

        re = self._get('/v1/statistics/sessions')
        self.assertEqual(200, re.status_code)

        sessions = re.json['sessions']
        self.assertEqual(1, len(sessions))
        session = sessions[0]

        self.assertEqual('test-session', session['session_key'])
        self.assertEqual(0, session['duration'])
        self.assertEqual(0, session['data_sent'])
        self.assertEqual(0, session['data_received'])
        self.assertEqual(0, session['data_transferred'])
        self.assertTrue(0 <= session['started'] < 1)
        self.assertEqual('Ongoing', session['status'])
        self.assertEqual('N/A', session['client_country_string'])

    def test_sessions_returns_limited_sessions(self):
        self._create_session('test-session-1')
        self._create_session('test-session-2')

        re = self._get('/v1/statistics/sessions', {'limit': 1})
        self.assertEqual(200, re.status_code)

        sessions = re.json['sessions']
        self.assertEqual(1, len(sessions))

    def test_sessions_returns_error_when_requesting_too_many_sessions(self):
        self._create_session('test-session-1')

        re = self._get('/v1/statistics/sessions', {'limit': 1000})
        self.assertEqual(400, re.status_code)

        self.assertEqual({'error': 'Too many sessions requested'}, re.json)

    def test_session_returns_session(self):
        self._create_session('test-session')

        re = self._get('/v1/statistics/sessions/test-session')
        self.assertEqual(200, re.status_code)
        session = re.json['session']
        self.assertEqual('test-session', session['session_key'])
        self.assertEqual(0, session['duration'])

    def test_session_returns_error_when_session_is_not_found(self):
        re = self._get('/v1/statistics/sessions/test-session')
        self.assertEqual(404, re.status_code)
        self.assertEqual({'error': 'Session not found'}, re.json)

    def _create_session(self, key):
        session = Session(key, 'openvpn')
        session.client_updated_at = datetime.utcnow()
        db.session.add(session)
