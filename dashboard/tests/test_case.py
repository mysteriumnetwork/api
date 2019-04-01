from flask_testing import TestCase
from dashboard.app import app, init_db
from models import db


class TestCase(TestCase):
    def create_app(self):
        db_config = {
            'host': 'localhost:33062',
            'name': 'myst_api',
            'user': 'myst_api',
            'passwd': 'myst_api'
        }

        init_db(db_config)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _get(self, url, params={}):
        return self.client.get(
            url,
            query_string=params,
        )
