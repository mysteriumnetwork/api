import os

DB_HOST = os.environ.get('DB_HOST') or "localhost"
DB_NAME = os.environ.get('DB_NAME')
USER = os.environ.get('DB_USER')
PASSWD = os.environ.get('DB_PASSWORD')