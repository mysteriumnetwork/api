import os

API_HOST = os.environ.get('API_HOST') or 'http://localhost:8001'

METRICS_CACHE_TIMEOUT = os.environ.get('METRICS_CACHE_TIMEOUT') \
                        or 5 * 60  # in seconds

DASHBOARD_CACHE_TIMEOUT = os.environ.get('DASHBOARD_CACHE_TIMEOUT') \
                        or 1 * 60  # in seconds

LEADERBOARD_CACHE_TIMEOUT = os.environ.get('LEADERBOARD_CACHE_TIMEOUT') \
                        or 15 * 60  # in seconds

VIEW_SESSIONS_CACHE_TIMEOUT = os.environ.get('VIEW_SESSIONS_CACHE_TIMEOUT') \
                        or 1 * 60  # in seconds
