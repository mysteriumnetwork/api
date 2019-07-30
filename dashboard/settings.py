import os

API_HOST = os.environ.get('API_HOST') or 'http://localhost:8001'

METRICS_CACHE_TIMEOUT = os.environ.get('METRICS_CACHE_TIMEOUT') \
                        or 5 * 60  # in seconds

DASHBOARD_CACHE_TIMEOUT = os.environ.get('DASHBOARD_CACHE_TIMEOUT') \
                        or 1 * 60  # in seconds

LEADERBOARD_CACHE_TIMEOUT = os.environ.get('LEADERBOARD_CACHE_TIMEOUT') \
                        or 15 * 60  # in seconds

VIEW_NODES_CACHE_TIMEOUT = os.environ.get('VIEW_NODES_CACHE_TIMEOUT') \
                        or 15 * 60  # in seconds

VIEW_SESSIONS_CACHE_TIMEOUT = os.environ.get('VIEW_SESSIONS_CACHE_TIMEOUT') \
                        or 1 * 60  # in seconds

VIEW_NODES_MAX_ROWS = os.environ.get('VIEW_NODES_MAX_ROWS') or 100

VIEW_SESSIONS_MAX_ROWS = os.environ.get('VIEW_SESSIONS_MAX_ROWS') or 100

NODE_AVAILABILITY_DAYS = os.environ.get('NODE_AVAILABILITY_DAYS') or 7
