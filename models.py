from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json


db = SQLAlchemy()


NODE_KEY_LIMIT = 42


class Node(db.Model):
    __tablename__ = 'node'
    node_key = db.Column(db.String(NODE_KEY_LIMIT), primary_key=True)
    ip = db.Column(db.String(45))
    connection_config = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, node_key):
        self.node_key = node_key
        self.created_at = datetime.utcnow()

    def get_status(self):
        # TODO: implement status checking
        return 'active'

    def get_service_proposals(self):
        try:
            config = json.loads(self.connection_config)
        except ValueError:
            return None

        service_proposal = config.get('service_proposal')
        if service_proposal is None:
            return None
        return [service_proposal]


class Session(db.Model):
    __tablename__ = 'session'

    session_key = db.Column(db.String(34), primary_key=True)
    node_key = db.Column(db.String(NODE_KEY_LIMIT))
    created_at = db.Column(db.DateTime)
    node_updated_at = db.Column(db.DateTime)
    client_updated_at = db.Column(db.DateTime)
    node_bytes_sent = db.Column(db.BigInteger)
    node_bytes_received = db.Column(db.BigInteger)
    client_bytes_sent = db.Column(db.BigInteger)
    client_bytes_received = db.Column(db.BigInteger)
    client_ip = db.Column(db.String(45))
    established = db.Column(db.Boolean)

    def __init__(self, session_key):
        self.session_key = session_key
        self.created_at = datetime.utcnow()
        self.established = False
        self.node_bytes_sent = 0
        self.node_bytes_received = 0
        self.client_bytes_sent = 0
        self.client_bytes_received = 0


class NodeAvailability(db.Model):
    __tablename__ = 'node_availability'
    #id = db.Column(db.String(34), primary_key=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_key = db.Column(db.String(34))
    date = db.Column(db.DateTime)

    def __init__(self, node_key):
        self.node_key = node_key
        self.date = datetime.utcnow()
        #self.id = self.node_key + self.date.strftime('%Y%m%d%H%M%S')


class Identity(db.Model):
    __tablename__ = 'identity'
    identity = db.Column(db.String(42), primary_key=True)
    created_at = db.Column(db.DateTime)

    def __init__(self, identity):
        self.identity = identity
        self.created_at = datetime.utcnow()
