import time
import uuid

from api.stats.db_queries.leaderboard import get_leaderboard_rows
from models import db, Node, IdentityRegistration, Session
from tests.test_case import TestCase
from datetime import datetime, timedelta
import json

now = datetime.utcnow()
second = timedelta(seconds=1)


def find(predicate, iterable):
    return next(filter(predicate, iterable), None)


def by_provider_id(provider_id):
    return lambda r: r.provider_id == provider_id


def fake_id():
    return str(uuid.uuid4())


class TestGetLeaderBoardRows(TestCase):
    # noinspection PyPep8Naming
    def setUp(self):
        super().setUp()
        db.engine.execute("ALTER EVENT evt_refresh_dwh_leaderboard ON SCHEDULE EVERY 5 SECOND")

    # noinspection PyPep8Naming
    def tearDown(self):
        super().tearDown()
        db.engine.execute("ALTER EVENT evt_refresh_dwh_leaderboard ON SCHEDULE EVERY 3 MINUTE")

    def test_correct_unique_users_and_service_type_match(self):
        provider_id = fake_id()
        self._create_identity_registration(provider_id, True)
        self._create_node(provider_id, 'openvpn', now)
        self._create_node(provider_id, 'other service', now)
        self._create_session(
            'session 1', 'consumer id 1',
            provider_id, 'openvpn', now, 1, 2
        )
        self._create_session(
            'session 2', 'consumer id 2',
            provider_id, 'openvpn', now, 3, 4
        )
        self._create_session(
            'session 3', 'consumer id 2',
            provider_id, 'openvpn', now, 0, 0
        )
        self._create_session(
            'session 4', 'consumer id 3',
            provider_id, 'other service', now, 20, 20
        )

        time.sleep(10)
        rows = get_leaderboard_rows(now - second, now + second)
        row = find(by_provider_id(provider_id), rows)
        self.assertIsNotNone(row)
        self.assertEqual(provider_id, row.provider_id)
        self.assertEqual(3, row.sessions_count)
        self.assertEqual(10, row.total_bytes)
        self.assertEqual(2, row.unique_users)

    def test_does_not_filter_non_bounty_programme(self):
        provider_id = fake_id()
        self._create_identity_registration(provider_id, False)
        self._create_node(provider_id, 'service x', now)
        self._create_node(provider_id, 'service y', now)
        self._create_session(
            'session 1', 'consumer id 1',
            provider_id, 'service x', now, 1, 2
        )
        self._create_session(
            'session 2', 'consumer id 1',
            provider_id, 'service y', now, 0, 0
        )
        self._create_session(
            'session 3', 'consumer id 2',
            provider_id, 'service y', now, 0, 0
        )
        self._create_session(
            'session 4', 'consumer id 3',
            provider_id, 'service y', now, 3, 4
        )
        rows = get_leaderboard_rows(now - second, now + second)
        row = find(by_provider_id(provider_id), rows)
        self.assertIsNone(row)

    def test_node_updated_at_mismatch(self):
        provider_id = fake_id()
        self._create_identity_registration(provider_id, True)
        self._create_node(provider_id, 'service 1', now - second)
        self._create_node(provider_id, 'service 2', now + second)
        self._create_session(
            'session 1', None,
            provider_id, 'service 1', now, 0, 0
        )
        self._create_session(
            'session 2', None,
            provider_id, 'service 2', now, 0, 0
        )
        rows = get_leaderboard_rows(now, now)
        row = find(by_provider_id(provider_id), rows)
        self.assertIsNone(row)

    def test_session_updated_at_mismatch(self):
        provider_id = fake_id()
        self._create_identity_registration(provider_id, True)
        self._create_node(provider_id, 'service', now)
        self._create_session(
            'session 1', None, provider_id,
            'service', now - second, 0, 0
        )
        self._create_session(
            'session 2', None, provider_id,
            'service', now + second, 0, 0
        )
        rows = get_leaderboard_rows(now, now)
        row = find(by_provider_id(provider_id), rows)
        self.assertIsNone(row)

    def test_node_has_no_sessions(self):
        provider_id = fake_id()
        self._create_identity_registration(provider_id, True)
        self._create_node(provider_id, 'service', now)
        rows = get_leaderboard_rows(now, now)
        row = find(by_provider_id(provider_id), rows)
        self.assertIsNone(row)

    def test_node_was_not_registered(self):
        provider_id = fake_id()
        self._create_node(provider_id, 'service', now)
        self._create_session(
            'session', None, provider_id,
            'service', now, 0, 0
        )
        rows = get_leaderboard_rows(now, now)
        row = find(by_provider_id(provider_id), rows)
        self.assertIsNone(row)

    def test_registered_without_node(self):
        provider_id = fake_id()
        self._create_identity_registration(provider_id, True)
        self._create_session(
            'session', None, provider_id,
            'service', now, 0, 0
        )
        rows = get_leaderboard_rows(now, now)
        row = find(by_provider_id(provider_id), rows)
        self.assertIsNone(row)

    @staticmethod
    def _create_identity_registration(id, bounty_program):
        ir = IdentityRegistration(id, '')
        ir.bounty_program = bounty_program
        db.session.add(ir)
        db.session.commit()

    @staticmethod
    def _create_node(node_key, service_type, updated_at,
                     node_type='residential'):
        node = Node(node_key, service_type)
        node.updated_at = updated_at
        node.node_type = node_type
        node.proposal = json.dumps({
            "service_definition": {
                "location": {"country": "IT"},
            }
        })
        db.session.add(node)
        db.session.commit()

    @staticmethod
    def _create_session(session_key, consumer_id, provider_id, service_type,
                        updated_at, bytes_sent, bytes_received):
        ses = Session(session_key, service_type)
        ses.consumer_id = consumer_id
        ses.node_key = provider_id
        ses.client_updated_at = updated_at
        ses.client_bytes_sent = bytes_sent
        ses.client_bytes_received = bytes_received
        db.session.add(ses)
        db.session.commit()
