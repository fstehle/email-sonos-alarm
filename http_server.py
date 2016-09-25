import logging

import os
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn, ForkingMixIn
import prometheus_client

import errno


class AssetsHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.serve_file(self.path, False)

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><body><p><a href="/metrics">Metrics</a></p></body></html>')
        elif self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
            self.end_headers()
            self.wfile.write(prometheus_client.generate_latest())
        else:
            self.serve_file(self.path, True)

    def serve_file(self, path, send_body=False):
        try:
            if self.path.endswith('.mp3'):
                f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets' + path))
                f_content = f.read()
                file_size = len(f_content)
                f.close()
                self.send_response(200)
                self.send_header('Content-type', 'audio/mpeg')
                self.send_header('Content-length', file_size)
                self.end_headers()
                if send_body:
                    self.wfile.write(f_content)
            else:
                self.send_error(404, 'File Not Found: %s' % path)

        except IOError, e:
            if e.errno == errno.ENOENT:
                self.send_error(404, 'File Not Found: %s' % path)
            else:
                raise

    def log_message(self, format, *args):
        logging.info('Serve HTTP request: %s' % format%args)

    def log_request(self, code='-', size='-'):
        if self.path == '/metrics' and code == 200:
            return
        self.log_message("%s' %s %s", self.requestline, str(code), str(size))


class HttpServer(ForkingMixIn, HTTPServer):
    def __init__(self, port):
        HTTPServer.__init__(self, ('', port), AssetsHandler)

    def finish_request(self, request, client_address):
        try:
            HTTPServer.finish_request(self, request, client_address)
        except IOError, e:
            if e.errno == errno.EPIPE:
                # Silence broken pipe error.
                pass
            else:
                raise
