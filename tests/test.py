import requests
import json


def test_node_reg():

    payload = {
        "service_proposal": {
            "id": 1,
            "format": "service-proposal/v1",
            "provider_id": "node1",
        }
    }

    re = requests.post(
        'http://127.0.0.1:5000/v1/node_register',
        data=json.dumps(payload)
    )

    print re.content
    re.json()


def test_client_create_session():
    payload = {
        'node_key': 'node key',
    }

    re = requests.post(
        'http://127.0.0.1:5000/v1/client_create_session',
        data = json.dumps(payload)
    )
    print re.content
    data = re.json()
    data['session_key']
    data['connection_config']


def test_node_get_session():
    payload = {
        'node_key': 'node key',
        'client_ip': '127.0.0.1',
    }
    re = requests.post(
        'http://127.0.0.1:5000/v1/node_get_session',
        data = json.dumps(payload)
    )
    print re.content
    data = re.json()
    data['session_key']


def test_node_send_stats():
    session = {
        'session_key': 'X2d9gyQk1j',
        'bytes_sent': 20,
        'bytes_received': 10,
    }

    payload = {
        'node_key': 'node key',
        'sessions': [session]
    }

    re = requests.post(
        'http://127.0.0.1:5000/v1/node_send_stats',
        data = json.dumps(payload)
    )

    print re.content
    data = re.json()
    for el in data['sessions']:
        el['is_session_valid']
        el['session_key']


def test_client_send_stats():
    payload = {
        'session_key': 'X2d9gyQk1j',
        'bytes_sent': 50,
        'bytes_received': 60,
    }

    re = requests.post(
        'http://127.0.0.1:5000/v1/client_send_stats',
        data = json.dumps(payload)
    )

    print re.content
    data = re.json()
    data['is_session_valid']
    data['session_key']



# test_node_reg()
# test_client_create_session()
# test_node_get_session()
# test_node_send_stats()
# test_client_send_stats()