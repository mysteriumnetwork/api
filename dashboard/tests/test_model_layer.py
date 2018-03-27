from dashboard.tests.test_case import TestCase
from dashboard import model_layer
import models


class TestModelLayer(TestCase):
    def test_get_db(self):
        db = model_layer.get_db()
        self.assertIsNotNone(db)
        self.assertEqual(models.db, db)

    def test_get_sessions_country_stats(self):
        self._create_session(1, 'country')
        self._create_session(2, 'country')
        self._create_session(3, None)

        results = model_layer.get_sessions_country_stats()
        self.assertEqual(2, len(results))
        self.assertEqual(2, results[0].count)
        self.assertEqual('country', results[0].client_country)
        self.assertEqual(1, results[1].count)
        self.assertEqual(None, results[1].client_country)

    @staticmethod
    def _create_session(session_key, country):
        session = models.Session(session_key)
        session.client_country = country
        model_layer.get_db().session.add(session)
