import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))  # noqa

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app
import settings

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(settings.APP_PORT)
IOLoop.instance().start()
