from dashboard.tests.test_case import TestCase
from dashboard.model_layer import (
    get_db,
    get_sessions_country_stats,
    get_node_data_transferred,
    get_sessions_count_by_date,
    get_node_hours_online,
    get_registered_nodes,
)
from datetime import datetime, timedelta
import models

now = datetime.utcnow()
second = timedelta(seconds=1)


class TestModelLayer(TestCase):
    def test_get_db(self):
        db = get_db()
        self.assertIsNotNone(db)
        self.assertEqual(models.db, db)

    def test_get_sessions_country_stats(self):
        self._create_session(1, 'country')
        self._create_session(2, 'country')
        self._create_session(3, None)

        results = get_sessions_country_stats()
        self.assertEqual(2, len(results))
        self.assertEqual(2, results[0].count)
        self.assertEqual('country', results[0].client_country)
        self.assertEqual(1, results[1].count)
        self.assertEqual(None, results[1].client_country)

    @staticmethod
    def _create_session(session_key, country):
        session = models.Session(session_key)
        session.client_country = country
        get_db().session.add(session)


class TestGetNodeDataTransferred(TestCase):
    def test_match_node_key_and_service_type(self):
        self._create_session(
            'session key 1', 'node key', 'service type', now,  1, 2
        )
        self._create_session(
            'session key 2', 'node key', 'service type', now, 3, 4
        )
        self._create_session(
            'session key 3', 'node key', 'other service type', now, -100, -100
        )
        self._create_session(
            'session key 4', 'other node key', 'service type', now, -100, -100
        )
        total_bytes = get_node_data_transferred(
            'node key',
            'service type',
            now,
            now + second
        )
        self.assertEqual(10, total_bytes)

    def test_where_dates_mismatch(self):
        self._create_session(
            'session key 1', 'node key', 'service type', now - second, 1, 2
        )
        self._create_session(
            'session key 2', 'node key', 'service type', now + second, 1, 2
        )
        total_bytes = get_node_data_transferred(
            'node key',
            'service type',
            now,
            now + second
        )
        self.assertEqual(0, total_bytes)

    @staticmethod
    def _create_session(session_key, node_key, service_type,
                        updated_at, bytes_sent, bytes_received):
        session = models.Session(session_key)
        session.node_key = node_key
        session.service_type = service_type
        session.client_updated_at = updated_at
        session.client_bytes_sent = bytes_sent
        session.client_bytes_received = bytes_received
        get_db().session.add(session)


class TestGetSessionsCountByDate(TestCase):
    def test_match_query_params(self):
        self._create_session(
            'session key 1', 'node key', 'service type', now
        )
        self._create_session(
            'session key 2', 'other node key', 'service type', now
        )
        self._create_session(
            'session key 3', 'node key', 'other service type', now
        )
        self._create_session(
            'session key 4', 'node key', 'service type', now - second
        )
        self._create_session(
            'session key 5', 'node key', 'service type', now + second
        )
        sessions_count = get_sessions_count_by_date(
            'node key',
            'service type',
            now,
            now + second
        )
        self.assertEqual(1, sessions_count)

    @staticmethod
    def _create_session(session_key, node_key, service_type, updated_at):
        session = models.Session(session_key)
        session.node_key = node_key
        session.service_type = service_type
        session.client_updated_at = updated_at
        get_db().session.add(session)


class TestGetNodeHoursOnline(TestCase):
    def test_returns_one_hour(self):
        for x in range(31):
            self._create_node_availability('node key', 'service type', now)

        hours = get_node_hours_online(
            'node key',
            'service type',
            now,
            now + second
        )
        self.assertEqual(1, hours)

    def test_not_match_query_params(self):
        for x in range(31):
            self._create_node_availability(
                'node key other', 'service type', now
            )

        for x in range(31):
            self._create_node_availability(
                'node key', 'service type other', now
            )

        for x in range(31):
            self._create_node_availability(
                'node key', 'service type', now + second
            )

        hours = get_node_hours_online(
            'node key',
            'service type',
            now,
            now + second
        )
        self.assertEqual(0, hours)

    @staticmethod
    def _create_node_availability(node_key, service_type, update_time):
        avail = models.NodeAvailability(node_key)
        avail.service_type = service_type
        avail.date = update_time
        get_db().session.add(avail)


class TestGetRegisteredNodes(TestCase):
    def test_match_query(self):
        self._create_identity_registration('node key')
        self._create_identity_registration('node key other')
        self._create_node('node key', 'type x', now)
        self._create_node('node key', 'type y', now)
        self._create_node('node key other', 'type 1', now - second)
        self._create_node('node key other', 'type 2', now + second)
        nodes = get_registered_nodes(now, now + second)
        self.assertEqual(2, len(nodes))
        self.assertEqual('node key', nodes[0].node_key)
        self.assertEqual('type x', nodes[0].service_type)
        self.assertEqual('node key', nodes[1].node_key)
        self.assertEqual('type y', nodes[1].service_type)

    @staticmethod
    def _create_identity_registration(id):
        ir = models.IdentityRegistration(id, '')
        get_db().session.add(ir)

    @staticmethod
    def _create_node(node_key, service_type, updated_at):
        node = models.Node(node_key, service_type)
        node.updated_at = updated_at
        get_db().session.add(node)
