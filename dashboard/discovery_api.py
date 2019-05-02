import requests
from json import JSONDecodeError
from typing import List, Optional

from dashboard.settings import API_HOST


REQUEST_TIMEOUT = 5


class ApiError(Exception):
    pass


def fetch_sessions(limit: int) -> List[any]:
    params = {'limit': limit}
    return _make_request('/v1/statistics/sessions', 'sessions', params)


def fetch_session(key: str) -> any:
    return _make_request('/v1/statistics/sessions/%s' % key, 'session')


def _make_request(path: str, response_key: str, params: any = None) -> any:
    try:
        response = requests.get(
            API_HOST + path,
            params,
            timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException as err:
        raise ApiError('Request failed') from err
    if response.status_code != 200:
        api_error = _parse_response_json_error(response)
        error_message = _format_response_error_message(
            response.status_code, api_error)
        raise ApiError(error_message)

    try:
        json = response.json()
    except JSONDecodeError:
        raise ApiError('Unable to parse response body json')
    if response_key not in json:
        raise ApiError('Missing response key in response json')
    return json[response_key]


def _parse_response_json_error(response: any) -> Optional[str]:
    try:
        json = response.json()
        if 'error' in json:
            return json['error']
    except JSONDecodeError:
        pass
    return None


def _format_response_error_message(
        status_code: str,
        error_message: Optional[str]) -> str:
    if error_message is not None:
        return 'Invalid response status code: %s, error: %s' % \
                  (status_code, error_message)
    return 'Invalid response status code: %s' % status_code
