from flask import Flask

import settings
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/{}'.format(
    settings.USER, settings.PASSWD, settings.DATABASE)
db.init_app(app)
with app.app_context():
    db.create_all()
