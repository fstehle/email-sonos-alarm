#!/usr/bin/env python
import threading
import unittest

import requests
from http_server import HttpServer

HTTP_PORT = 8080
TEST_FILE = "home_phone_ringing_soundbible.com-476855293.mp3"
TEST_FILE_SIZE = 187920

class TestHttpServer(unittest.TestCase):
    httpd = None

    @classmethod
    def setUpClass(cls):
        cls.httpd = HttpServer(HTTP_PORT)
        server_thread = threading.Thread(name="HTTPServerThread", target=cls.httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def test_mp3_download(self):
        url = "http://localhost:%i/%s" % (HTTP_PORT, TEST_FILE)
        r = requests.get(url)

        self.assertEqual(r.status_code, 200)

        self.assertEqual(r.headers['content-type'], "audio/mpeg")
        self.assertEqual(r.headers['content-length'], str(len(r.content)))

    def test_mp3_not_found(self):
        url = "http://localhost:%i/%s" % (HTTP_PORT, "foo")
        r = requests.get(url)

        self.assertEqual(r.status_code, 404)

    def test_mp3_head_request(self):
        url = "http://localhost:%i/%s" % (HTTP_PORT, TEST_FILE)
        r = requests.head(url)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['content-type'], "audio/mpeg")
        self.assertEqual(r.headers['content-length'], str(TEST_FILE_SIZE))

if __name__ == '__main__':
    unittest.main()
