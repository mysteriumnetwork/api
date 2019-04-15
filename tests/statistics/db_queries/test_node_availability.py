from api.statistics.db_queries.node_availability import get_node_hours_online
from tests.test_case import TestCase
from models import db, NodeAvailability
from datetime import datetime, timedelta

now = datetime.utcnow()
second = timedelta(seconds=1)


class TestNodeAvailability(TestCase):
    def test_result_is_rounded_to_hour(self):
        for x in range(31):
            self._create_node_availability('node key', 'service type', now)

        hours = get_node_hours_online(
            'node key',
            'service type',
            now - second,
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
            now
        )
        self.assertEqual(0, hours)

    @staticmethod
    def _create_node_availability(provider_id, service_type, update_time):
        avail = NodeAvailability(provider_id)
        avail.service_type = service_type
        avail.date = update_time
        db.session.add(avail)
