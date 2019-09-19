import json
from datetime import datetime, timedelta
from models import db, Session
from tests.test_case import TestCase
from tests.utils import (
    build_test_authorization,
    setting,
)


class TestSessions(TestCase):
    def test_session_stats_create_without_session_record(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
            'consumer_country': 'country'
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        session = Session.query.get('123')
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertEqual(auth['public_address'], session.consumer_id)
        self.assertEqual('8.8.8.X', session.client_ip)
        self.assertEqual('country', session.client_country)
        self.assertEqual('0x1', session.node_key)
        self.assertEqual('openvpn', session.service_type)

    def test_session_stats_create_with_type(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
            'consumer_country': 'country',
            'service_type': 'dummy'
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        session = Session.query.get('123')
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertEqual(auth['public_address'], session.consumer_id)
        self.assertEqual('8.8.8.X', session.client_ip)
        self.assertEqual('country', session.client_country)
        self.assertEqual('0x1', session.node_key)
        self.assertEqual('dummy', session.service_type)

    def test_session_stats_without_session_record_and_consumer_country(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)
        session = Session.query.get('123')
        self.assertEqual('', session.client_country)

    def test_session_stats_create_without_session_record_with_unknown_ip(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
            remote_addr='127.0.0.1',
        )

        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        session = Session.query.get('123')
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertEqual(auth['public_address'], session.consumer_id)
        self.assertEqual('127.0.0.X', session.client_ip)
        self.assertEqual('', session.client_country)
        self.assertEqual('0x1', session.node_key)

    def test_session_stats_create_successful(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))

        session = Session('123', 'openvpn')
        session.consumer_id = auth['public_address']
        db.session.add(session)
        db.session.commit()

        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(200, re.status_code)
        self.assertEqual({}, re.json)

        session = Session.query.get('123')
        self.assertEqual(20, session.client_bytes_sent)
        self.assertEqual(40, session.client_bytes_received)
        self.assertIsNotNone(session.client_updated_at)
        self.assertIsNone(session.node_key)

    def test_session_stats_create_with_different_consumer_id(self):
        session = Session('123', 'openvpn')
        session.consumer_id = 'different'
        db.session.add(session)
        db.session.commit()

        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(403, re.status_code)
        self.assertEqual(
            {'error': 'session identity does not match current one'},
            re.json
        )

        session = Session.query.get('123')
        self.assertEqual(0, session.client_bytes_sent)

    def test_session_stats_create_with_negative_values(self):
        auth = build_test_authorization()
        re = self._post(
            '/v1/sessions/123/stats',
            {
                'bytes_sent': -20,
                'bytes_received': 40,
                'provider_id': '0x1',
            },
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_sent missing or value is not unsigned int'},
            re.json
        )

        re = self._post(
            '/v1/sessions/123/stats',
            {
                'bytes_sent': 20,
                'bytes_received': -40,
                'provider_id': '0x1',
            },
            headers=auth['headers']
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_received missing or value is not unsigned int'},
            re.json
        )

        sessions = Session.query.all()
        self.assertEqual(0, len(sessions))

    def test_session_stats_without_provider_id(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'provider_id missing'},
            re.json
        )

        session = Session.query.get('123')
        self.assertIsNone(session)

    def test_session_stats_without_bytes_sent(self):
        payload = {
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_sent missing or value is not unsigned int'},
            re.json
        )

        sessions = Session.query.all()
        self.assertEqual(0, len(sessions))

    def test_session_stats_without_bytes_received(self):
        payload = {
            'bytes_sent': 20,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )

        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'bytes_received missing or value is not unsigned int'},
            re.json
        )

        sessions = Session.query.all()
        self.assertEqual(0, len(sessions))

    def test_session_stats_when_session_has_expired(self):
        payload = {
            'bytes_sent': 20,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))
        session = Session('123', 'openvpn')
        session.consumer_id = auth['public_address']
        session.created_at = datetime.utcnow() - timedelta(minutes=11)
        session.client_updated_at = None
        db.session.add(session)
        db.session.commit()
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'session has expired'},
            re.json
        )

        # update client_updated_at in that way session should not expire
        session.client_updated_at = datetime.utcnow() - timedelta(minutes=9)
        db.session.add(session)
        db.session.commit()
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(200, re.status_code)

        # update client_updated_at in that way session should expire
        session.client_updated_at = datetime.utcnow() - timedelta(minutes=11)
        db.session.add(session)
        db.session.commit()
        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(400, re.status_code)
        self.assertEqual(
            {'error': 'session has expired'},
            re.json
        )


    def test_session_stats_exceeding_sent_limit(self):
        payload = {
            'bytes_sent': round((1000000000 / 8 * 60) * 5),
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))

        session = Session('123', 'openvpn')
        session.consumer_id = auth['public_address']
        db.session.add(session)
        db.session.commit()

        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(418, re.status_code)
        self.assertEqual({}, re.json)


    def test_session_stats_exceeding_received_limit(self):
        payload = {
            'bytes_sent': 5,
            'bytes_received': round(40 + (1000000000 / 8 * 60) + 1),
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))

        session = Session('123', 'openvpn')
        session.consumer_id = auth['public_address']
        session.client_bytes_received = 40
        db.session.add(session)
        db.session.commit()

        re = self._post(
            '/v1/sessions/123/stats',
            payload,
            headers=auth['headers'],
        )
        self.assertEqual(418, re.status_code)
        self.assertEqual({}, re.json)
      

    def test_session_stats_rate_limited(self):
        payload = {
            'bytes_sent': 5,
            'bytes_received': 40,
            'provider_id': '0x1',
        }
        auth = build_test_authorization(json.dumps(payload))

        session = Session('123', 'openvpn')
        session.consumer_id = auth['public_address']
        db.session.add(session)
        db.session.commit()

        with setting('THROTTLE_SESSION_STATS', True):
            re = self._post(
                '/v1/sessions/123/stats',
                payload,
                headers=auth['headers'],
            )
            self.assertEqual(200, re.status_code)
            self.assertEqual({}, re.json)

            re = self._post(
                '/v1/sessions/123/stats',
                payload,
                headers=auth['headers'],
            )
            self.assertEqual(429, re.status_code)
            self.assertEqual({'error': 'too many requests'}, re.json)
