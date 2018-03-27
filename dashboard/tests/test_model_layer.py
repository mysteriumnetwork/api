from dashboard.tests.test_case import TestCase
from dashboard import model_layer
import models


class TestModelLayer(TestCase):
    def test_get_db(self):
        db = model_layer.get_db()
        self.assertIsNotNone(db)
        self.assertEqual(models.db, db)
