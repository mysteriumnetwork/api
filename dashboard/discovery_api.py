import requests
from json import JSONDecodeError
from typing import List

from dashboard.settings import API_HOST


class ApiError(Exception):
    pass


def fetch_sessions(limit: int) -> List[any]:
    params = {'limit': limit}
    json = _make_request('/v1/statistics/sessions', params)
    return json['sessions']


def fetch_session(key: str) -> any:
    json = _make_request('/v1/statistics/sessions/%s' % key)
    return json['session']


def _make_request(path: str, params: any = None) -> any:
    response = requests.get(API_HOST + path, params)
    if response.status_code != 200:
        raise ApiError()

    try:
        json = response.json()
    except JSONDecodeError:
        raise ApiError('Unable to parse response body json')
    return json
