from flask_testing import TestCase
import app as main
import json


class TestCase(TestCase):
    def create_app(self):
        main.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
        main.db.init_app(main.app)
        return main.app

    def setUp(self):
        main.db.create_all()

    def tearDown(self):
        main.db.session.remove()
        main.db.drop_all()

    # TODO: find better place to move constant
    REMOTE_ADDR = '8.8.8.8'

    def _get(self, url, params={}):
        return self.client.get(
            url,
            query_string=params,
            environ_base={'REMOTE_ADDR': self.REMOTE_ADDR}
        )

    def _post(self, url, payload, headers=None, remote_addr=None):
        return self.client.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            environ_base={'REMOTE_ADDR': remote_addr or self.REMOTE_ADDR}
        )
