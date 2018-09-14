import os
from distutils import util

APP_PORT = os.environ.get('APP_PORT') or 80

DB_HOST = os.environ.get('DB_HOST') or 'localhost'
DB_NAME = os.environ.get('DB_NAME') or ''
USER = os.environ.get('DB_USER') or ''
PASSWD = os.environ.get('DB_PASSWORD') or ''

# util.strtobool
# True values are y, yes, t, true, on and 1;
# False values are n, no, f, false, off and 0.
# Raises ValueError if val is anything else.
RESTRICT_BY_IP_ENABLED = bool(util.strtobool(
    os.environ.get('RESTRICT_BY_IP_ENABLED') or 'no'
))
ALLOWED_IP_ADDRESSES = (
    os.environ.get('ALLOWED_IP_ADDRESSES') or ''
).split(',')

ETHER_RPC_URL = os.environ.get('ETHER_RPC_URL') \
                              or 'https://ropsten.infura.io/'

ETHER_MINING_MODE = os.environ.get('ETHER_MINING_MODE') or 'pow'
if ETHER_MINING_MODE not in ['pow', 'poa']:
    raise Exception('Not supported ether mining mode')

IDENTITY_CONTRACT = os.environ.get('IDENTITY_CONTRACT') \
                    or '0xbe5F9CCea12Df756bF4a5Baf4c29A10c3ee7C83B'
