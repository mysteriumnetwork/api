from dashboard.db_queries.leaderboard import get_leaderboard_rows
from models import db, Node, IdentityRegistration, Session
from dashboard.tests.test_case import TestCase
from datetime import datetime, timedelta

now = datetime.utcnow()
second = timedelta(seconds=1)


class TestGetLeaderBoardRows(TestCase):
    def test_correct_unique_users_and_service_type_match(self):
        self._create_identity_registration('provider id')
        self._create_node('provider id', 'service x', now)
        self._create_node('provider id', 'service y', now)
        self._create_session(
            'session 1', 'consumer id 1',
            'provider id', 'service x', now, 1, 2
        )
        self._create_session(
            'session 2', 'consumer id 1',
            'provider id', 'service y', now, 0, 0
        )
        self._create_session(
            'session 3', 'consumer id 2',
            'provider id', 'service y', now, 0, 0
        )
        self._create_session(
            'session 4', 'consumer id 3',
            'provider id', 'service y', now, 3, 4
        )
        rows = get_leaderboard_rows(now, now + second)
        self.assertEqual(1, len(rows))
        self.assertEqual('provider id', rows[0].provider_id)
        self.assertEqual(4, rows[0].sessions_count)
        self.assertEqual(10, rows[0].total_bytes)
        self.assertEqual(3, rows[0].unique_users)

    def test_node_updated_at_mismatch(self):
        self._create_identity_registration('provider id')
        self._create_node('provider id', 'service 1', now - second)
        self._create_node('provider id', 'service 2', now + second)
        self._create_session(
            'session 1', None,
            'provider id', 'service 1', now, 0, 0
        )
        self._create_session(
            'session 2', None,
            'provider id', 'service 2', now, 0, 0
        )
        rows = get_leaderboard_rows(now, now + second)
        self.assertEqual(0, len(rows))

    def test_session_updated_at_mismatch(self):
        self._create_identity_registration('provider id')
        self._create_node('provider id', 'service', now)
        self._create_session(
            'session 1', None, 'provider id',
            'service', now - second, 0, 0
        )
        self._create_session(
            'session 2', None, 'provider id',
            'service', now + second, 0, 0
        )
        rows = get_leaderboard_rows(now, now + second)
        self.assertEqual(0, len(rows))

    def test_node_has_no_sessions(self):
        self._create_identity_registration('provider id')
        self._create_node('provider id', 'service', now)
        rows = get_leaderboard_rows(now, now + second)
        self.assertEqual(0, len(rows))

    def test_node_was_not_registered(self):
        self._create_node('provider id', 'service', now)
        self._create_session(
            'session', None, 'provider id',
            'service', now, 0, 0
        )
        rows = get_leaderboard_rows(now, now + second)
        self.assertEqual(0, len(rows))

    def test_registered_without_node(self):
        self._create_identity_registration('provider id')
        self._create_session(
            'session', None, 'provider id',
            'service', now, 0, 0
        )
        rows = get_leaderboard_rows(now, now + second)
        self.assertEqual(0, len(rows))

    @staticmethod
    def _create_identity_registration(id):
        ir = IdentityRegistration(id, '')
        db.session.add(ir)
        db.session.commit()

    @staticmethod
    def _create_node(node_key, service_type, updated_at):
        node = Node(node_key, service_type)
        node.updated_at = updated_at
        db.session.add(node)
        db.session.commit()

    @staticmethod
    def _create_session(session_key, consumer_id, provider_id, service_type,
                        updated_at, bytes_sent, bytes_received):
        ses = Session(session_key)
        ses.consumer_id = consumer_id
        ses.node_key = provider_id
        ses.service_type = service_type
        ses.client_updated_at = updated_at
        ses.client_bytes_sent = bytes_sent
        ses.client_bytes_received = bytes_received
        db.session.add(ses)
        db.session.commit()
