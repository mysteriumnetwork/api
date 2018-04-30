from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json


db = SQLAlchemy()


IDENTITY_LENGTH_LIMIT = 42
SESSION_KEY_LIMIT = 36
AVAILABILITY_TIMEOUT = timedelta(minutes=2)


class Node(db.Model):
    __tablename__ = 'node'
    node_key = db.Column(db.String(IDENTITY_LENGTH_LIMIT), primary_key=True)
    ip = db.Column(db.String(45))
    connection_config = db.Column(db.Text)
    proposal = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, node_key):
        self.node_key = node_key
        self.created_at = datetime.utcnow()

    def is_active(self):
        return _is_active(self.updated_at)

    def mark_activity(self):
        self.updated_at = datetime.utcnow()

    def mark_inactive(self):
        # TODO this is bad, need a good way to save unregistered node state
        self.updated_at = datetime.utcnow() - AVAILABILITY_TIMEOUT

    def get_service_proposals(self):
        try:
            proposal = json.loads(self.proposal)
        except ValueError:
            return []
        return [proposal]

    def get_country_from_service_proposal(self):
        proposals = self.get_service_proposals()

        try:
            pr = proposals[0]
            return pr['service_definition']['location_originate']['country']
        except KeyError:
            return None


class Session(db.Model):
    __tablename__ = 'session'

    session_key = db.Column(db.String(SESSION_KEY_LIMIT), primary_key=True)
    node_key = db.Column(db.String(IDENTITY_LENGTH_LIMIT))
    created_at = db.Column(db.DateTime)
    node_updated_at = db.Column(db.DateTime)
    client_updated_at = db.Column(db.DateTime)
    node_bytes_sent = db.Column(db.BigInteger)
    node_bytes_received = db.Column(db.BigInteger)
    consumer_id = db.Column(db.String(IDENTITY_LENGTH_LIMIT))
    client_bytes_sent = db.Column(db.BigInteger)
    client_bytes_received = db.Column(db.BigInteger)
    client_ip = db.Column(db.String(45))
    client_country = db.Column(db.String(255))
    established = db.Column(db.Boolean)

    def __init__(self, session_key):
        self.session_key = session_key
        self.created_at = datetime.utcnow()
        self.established = False
        self.node_bytes_sent = 0
        self.node_bytes_received = 0
        self.client_bytes_sent = 0
        self.client_bytes_received = 0

    def is_active(self):
        return _is_active(self.client_updated_at)


class NodeAvailability(db.Model):
    __tablename__ = 'node_availability'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_key = db.Column(db.String(IDENTITY_LENGTH_LIMIT))
    date = db.Column(db.DateTime)

    def __init__(self, node_key):
        self.node_key = node_key
        self.date = datetime.utcnow()


class Identity(db.Model):
    __tablename__ = 'identity'
    identity = db.Column(db.String(IDENTITY_LENGTH_LIMIT), primary_key=True)
    created_at = db.Column(db.DateTime)

    def __init__(self, identity):
        self.identity = identity
        self.created_at = datetime.utcnow()


def _is_active(last_update_time):
    if last_update_time is None:
        return False
    return last_update_time > datetime.utcnow() - AVAILABILITY_TIMEOUT
