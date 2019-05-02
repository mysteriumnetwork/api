import json
from dashboard.tests.test_case import TestCase
from models import db, Session, Node
from datetime import datetime
import responses
import requests


class TestEndpoints(TestCase):
    mocked_session = {
        'session_key': 'test-session',
        'duration': 4,
        'data_sent': 5,
        'data_received': 3,
        'data_transferred': 8,
        'started': 1.23,
        'status': 'Ongoing',
        'client_country_string': 'N/A'
    }

    def setUp(self):
        super().setUp()
        session = Session('test-session', 'test service')
        session.client_updated_at = datetime.utcnow()
        db.session.add(session)

    @responses.activate
    def test_home_succeeds(self):
        self.mock_sessions(200, {'sessions': [self.mocked_session]})
        re = self._get('/')
        self.assertEqual(200, re.status_code)

    @responses.activate
    def test_home_handles_api_error(self):
        self.mock_sessions(500, {'error': 'mock error'})
        re = self._get('/')
        self.assertEqual(503, re.status_code)

    @responses.activate
    def test_home_handles_api_invalid_json_response(self):
        self.mock_sessions(200, body='mock response')
        re = self._get('/')
        self.assertEqual(503, re.status_code)

    @responses.activate
    def test_home_handles_api_invalid_json_response(self):
        self.mock_sessions(200, body='mock response')
        re = self._get('/')
        self.assertEqual(503, re.status_code)

    @responses.activate
    def test_sessions_succeds(self):
        self.mock_sessions(200, {'sessions': [self.mocked_session]})
        re = self._get('/sessions')
        self.assertEqual(200, re.status_code)

    @responses.activate
    def test_sessions_handles_api_error(self):
        self.mock_sessions(500)
        re = self._get('/sessions')
        self.assertEqual(503, re.status_code)

    @responses.activate
    def test_sessions_handles_missing_data(self):
        self.mock_sessions(200, {})
        re = self._get('/sessions')
        self.assertEqual(503, re.status_code)

    @responses.activate
    def test_session_succeeds(self):
        responses.add(
            responses.GET,
            'http://localhost:8001/v1/statistics/sessions/test-session',
            json={'session': self.mocked_session},
        )
        re = self._get('/session/test-session')
        self.assertEqual(200, re.status_code)

    @responses.activate
    def test_session_handles_request_exception(self):
        responses.add(
            responses.GET,
            'http://localhost:8001/v1/statistics/sessions/test-session',
            body=requests.exceptions.RequestException('Mock request exception')
        )
        re = self._get('/session/test-session')
        self.assertEqual(503, re.status_code)
        body = re.get_data(as_text=True)
        self.assertIn('Request to discovery failed', body)

    @responses.activate
    def test_session_handles_api_error(self):
        responses.add(
            responses.GET,
            'http://localhost:8001/v1/statistics/sessions/test-session',
            status=500
        )
        re = self._get('/session/test-session')
        self.assertEqual(503, re.status_code)

    def test_node_succeeds(self):
        node = Node('test-node', 'openvpn')
        node.proposal = json.dumps({
            "id": 1,
            "format": "service-proposal/v1",
            "provider_id": 'test-node',
        })
        node.mark_activity()
        db.session.add(node)

        session = Session('test-node-session', 'openvpn')
        session.client_updated_at = datetime.utcnow()
        session.node_key = 'test-node'
        db.session.add(session)

        re = self._get('/node/test-node/openvpn')
        self.assertEqual(200, re.status_code)

    def test_leaderboard_succeeds(self):
        re = self._get('/leaderboard')
        self.assertEqual(200, re.status_code)

    def test_leaderboard_get_page_succeeds(self):
        re = self._get('/leaderboard', {'page': 1})
        self.assertEqual(200, re.status_code)

    def test_leaderboard_handle_invalid_int_as_page_number(self):
        re = self._get('/leaderboard', {'page': 'a'})
        self.assertEqual(400, re.status_code)

    def test_leaderboard_handle_invalid_page_number(self):
        re = self._get('/leaderboard', {'page': 0})
        self.assertEqual(400, re.status_code)

    def mock_sessions(self, status=None, json=None, body=None):
        responses.add(
            responses.GET,
            'http://localhost:8001/v1/statistics/sessions',
            status=status,
            json=json,
            body=body
        )
