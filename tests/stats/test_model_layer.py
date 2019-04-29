from tests.test_case import TestCase
from api.stats.model_layer import get_sessions_country_stats
from datetime import datetime, timedelta
from models import db, Session

now = datetime.utcnow()
second = timedelta(seconds=1)


class TestModelLayer(TestCase):
    def test_get_sessions_country_stats(self):
        self._create_session(1, 'country')
        self._create_session(2, 'country')
        self._create_session(3, None)

        results = get_sessions_country_stats()
        self.assertEqual(2, len(results))
        self.assertEqual(2, results[0].count)
        self.assertEqual('country', results[0].client_country)
        self.assertEqual(1, results[1].count)
        self.assertEqual(None, results[1].client_country)

    @staticmethod
    def _create_session(session_key, country):
        session = Session(session_key, 'openvpn')
        session.client_country = country
        db.session.add(session)
