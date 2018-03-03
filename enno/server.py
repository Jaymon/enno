# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from .compat import *
from threading import Thread


class CallbackHandler(SimpleHTTPRequestHandler):
    @property
    def query(self):
        query = {}
        if "?" in self.path:
            query = self.parse_querystr(self.path[self.path.find("?")+1:])
        return query

    def parse_querystr(self, s):
        d = {}
        for k, kv in urlparse.parse_qs(s, True, strict_parsing=True).items():
            if len(kv) > 1:
                d[k] = kv
            else:
                d[k] = kv[0]
        return d

    def end_headers(self):
        self.headers_sent = True
        return SimpleHTTPRequestHandler.end_headers(self)

    def do_HEAD(self):
        """handle HEAD requests, since this is defined in parent it must be overridden"""
        return self.do()

    def do_GET(self):
        """handle GET requests, since this is defined in parent it must be overridden"""
        return self.do()

    def __getattr__(self, k):
        """handle any other METHOD requests"""
        if k.startswith("do_"):
            return self.do
        else:
            raise AttributeError(k)

    def do(self):
        ret = None
        self.headers_sent = False

        try:
            try:
                ret = self.server.callback(self)
            except KeyError:
                if not self.headers_sent:
                    self.send_error(501, "Unsupported method {}".format(self.command))
                return

        except Exception as e:
            if not self.headers_sent:
                self.send_error(500, "{} - {}".format(e.__class__.__name__, e))

        else:
            if ret is None or ret == "" or ret == 0:
                if not self.headers_sent:
                    self.send_response(204)
                    self.end_headers()

            else:
                if not self.headers_sent:
                    self.send_response(200)
                    self.end_headers()

                if is_py2:
                    self.wfile.write(ret)
                else:
                    self.wfile.write(bytes(ret, "utf-8"))


class AuthServer(HTTPServer):
    """
    https://github.com/python/cpython/blob/2.7/Lib/BaseHTTPServer.py#L102
    https://github.com/python/cpython/blob/2.7/Lib/SocketServer.py
    https://docs.python.org/2/library/simplehttpserver.html
    """
    @property
    def hostname(self):
        return self.server_name

    @property
    def port(self):
        return self.server_port

    @property
    def netloc(self):
        netloc = "http://{}:{}".format(self.hostname, self.port)
        return netloc

    @property
    def started(self):
        """Returns True if the webserver has been started"""
        try:
            ret = True if self.thread else False
        except AttributeError:
            ret = False
        return ret

    def __init__(self, callback, hostname="", port=0, handler_cls=CallbackHandler):
        HTTPServer.__init__(self, (hostname, port), handler_cls)
        self.callback = callback

    def __enter__(self):
        """Allows webserver to be used with "with" keyword"""
        self.start()
        return self

    def __exit__(self, esc_type, esc_val, traceback):
        """Allows webserver to be used with "with" keyword"""
        self.stop()

    def start(self):
        """Start the webserver"""
        if self.started: return
        server = self

        def target():
            try:
                server.serve_forever()
            except Exception as e:
                pout.v(e)
                raise

        th = Thread(target=target)
        th.daemon = True
        th.start()
        self.thread = th

    def stop(self):
        """stop the webserver"""
        if self.started:
            self.shutdown()
            self.thread = None

