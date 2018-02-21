from datetime import datetime, timedelta

from tests.test_case import TestCase
from models import Session, AVAILABILITY_TIMEOUT


class TestSession(TestCase):
    def test_is_active(self):
        session = Session("session")

        self.assertFalse(session.is_active())

        session.client_updated_at = datetime.utcnow()
        self.assertTrue(session.is_active())

        timeout_delta = AVAILABILITY_TIMEOUT + timedelta(minutes=1)
        session.client_updated_at = datetime.utcnow() - timeout_delta
        self.assertFalse(session.is_active())
