import requests
from json import JSONDecodeError
from typing import List

from dashboard.settings import API_HOST


class ApiError(Exception):
    pass


def fetch_sessions(limit: int) -> List[any]:
    params = {'limit': limit}
    return _make_request('/v1/statistics/sessions', 'sessions', params)


def fetch_session(key: str) -> any:
    return _make_request('/v1/statistics/sessions/%s' % key, 'session')


def _make_request(path: str, response_key: str, params: any = None) -> any:
    response = requests.get(API_HOST + path, params)
    if response.status_code != 200:
        raise ApiError(
            'Invalid response status code: %s' % response.status_code)

    try:
        json = response.json()
    except JSONDecodeError:
        raise ApiError('Unable to parse response body json')
    if response_key not in json:
        raise ApiError('Missing response key in response json')
    return json[response_key]
