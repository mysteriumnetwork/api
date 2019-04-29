import sys
from os import path
api_path = path.dirname(path.dirname(path.abspath(__file__)))  # noqa
sys.path.append(api_path)  # noqa

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app
from api import settings

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(settings.APP_PORT)
IOLoop.instance().start()
