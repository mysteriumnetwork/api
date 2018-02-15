import os

APP_PORT = os.environ.get('APP_PORT') or 80

DB_HOST = os.environ.get('DB_HOST') or "localhost"
DB_NAME = os.environ.get('DB_NAME')
USER = os.environ.get('DB_USER')
PASSWD = os.environ.get('DB_PASSWORD')
