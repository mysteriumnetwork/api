from datetime import datetime

from tests.test_case import TestCase
from models import db, Session


class TestStatistics(TestCase):
    def test_sessions_returns_sessions(self):
        session = Session('123', 'openvpn')
        session.client_updated_at = datetime.utcnow()
        db.session.add(session)

        re = self._get('/v1/statistics/sessions')
        self.assertEqual(200, re.status_code)

        sessions = re.json['sessions']
        self.assertEqual(1, len(sessions))
        session = sessions[0]

        self.assertEqual('123', session['session_key'])
        self.assertEqual(0, session['duration'])
        self.assertEqual(0, session['data_sent'])
        self.assertEqual(0, session['data_received'])
        self.assertEqual(0, session['data_transferred'])
        self.assertTrue(0 <= session['started'] < 1)
        self.assertEqual('Ongoing', session['status'])
        self.assertEqual('N/A', session['client_country_string'])

    def test_sessions_returns_limited_sessions(self):
        session = Session('first', 'openvpn')
        session.client_updated_at = datetime.utcnow()
        db.session.add(session)

        session = Session('second', 'openvpn')
        session.client_updated_at = datetime.utcnow()
        db.session.add(session)

        re = self._get('/v1/statistics/sessions', {'limit': 1})
        self.assertEqual(200, re.status_code)

        sessions = re.json['sessions']
        self.assertEqual(1, len(sessions))
