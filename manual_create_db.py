from flask import Flask

import settings
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    settings.USER, settings.PASSWD, settings.DB_HOST, settings.DB_NAME)
db.init_app(app)
with app.app_context():
    db.create_all()
