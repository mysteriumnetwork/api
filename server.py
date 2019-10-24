from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from api.node_availability_worker import start_node_availability_worker, node_availability_queue
from app import app, init_db
from api import settings
from models import db

print('starting server')
init_db()
start_node_availability_worker(db.get_engine(app), node_availability_queue)

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(settings.APP_PORT)
IOLoop.instance().start()
