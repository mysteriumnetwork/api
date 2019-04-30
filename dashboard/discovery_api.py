import requests
from json import JSONDecodeError
from typing import List

from dashboard.settings import API_HOST


class ApiError(Exception):
    pass


def fetch_sessions(limit: int) -> List[any]:
    params = {'limit': limit}
    response = requests.get('%s/v1/statistics/sessions' % API_HOST, params)
    if response.status_code != 200:
        raise ApiError()

    try:
        json = response.json()
    except JSONDecodeError:
        raise ApiError('Unable to parse response body json')
    return json['sessions']
