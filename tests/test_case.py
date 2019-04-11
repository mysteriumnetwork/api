from flask_testing import TestCase
from app import app, init_db
import json
from models import db


class TestCase(TestCase):
    def create_app(self):
        init_db()
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # TODO: find better place to move constant
    REMOTE_ADDR = '8.8.8.8'

    def _get(self, url, params={}, headers=None):
        return self.client.get(
            url,
            query_string=params,
            headers=headers,
            environ_base={'REMOTE_ADDR': self.REMOTE_ADDR}
        )

    def _post(self, url, payload, headers=None, remote_addr=None):
        return self.client.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            environ_base={'REMOTE_ADDR': remote_addr or self.REMOTE_ADDR}
        )

    def _put(self, url, payload, headers=None):
        return self.client.put(
            url,
            data=json.dumps(payload),
            headers=headers,
            environ_base={'REMOTE_ADDR': self.REMOTE_ADDR}
        )
