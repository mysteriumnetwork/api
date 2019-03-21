from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app, init_db
import settings

print('starting server')
init_db()

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(settings.APP_PORT)
IOLoop.instance().start()
