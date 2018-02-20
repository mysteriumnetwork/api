import os
from distutils import util

APP_PORT = os.environ.get('APP_PORT') or 80

DB_HOST = os.environ.get('DB_HOST') or "localhost"
DB_NAME = os.environ.get('DB_NAME')
USER = os.environ.get('DB_USER')
PASSWD = os.environ.get('DB_PASSWORD')

# util.strtobool
# True values are y, yes, t, true, on and 1;
# False values are n, no, f, false, off and 0.
# Raises ValueError if val is anything else.
RESTRICT_BY_IP_ENABLED = util.strtobool(
    os.environ.get('RESTRICT_BY_IP_ENABLED') or 'no'
)
ALLOWED_IP_ADDRESSES = os.environ.get('ALLOWED_IP_ADDRESSES') or ''
