from dashboard.tests.test_case import TestCase
from dashboard import model_layer
import models


class TestModelLayer(TestCase):
    def test_get_db(self):
        db = model_layer.get_db()
        self.assertIsNotNone(db)
        self.assertEqual(models.db, db)

    def test_get_sessions_country_stats(self):
        db = model_layer.get_db()
        s1 = models.Session('1')
        s1.client_country = 'country'
        db.session.add(s1)
        s2 = models.Session('2')
        s2.client_country = 'country'
        db.session.add(s2)
        s2 = models.Session('3')
        s2.client_country = None
        db.session.add(s2)

        results = model_layer.get_sessions_country_stats()
        self.assertEqual(2, results[0].count)
        self.assertEqual('country', results[0].client_country)
        self.assertEqual(1, results[1].count)
        self.assertEqual(None, results[1].client_country)
