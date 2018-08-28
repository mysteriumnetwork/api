from flask_testing import TestCase
import app as main


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
