#!/usr/bin/env python
import argparse
import logging
import threading
import time

import os
from http_server import HttpServer
from mail_fetcher import MailFetcher
from sonos_alarm import SonosAlarm

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--port', metavar='P', type=int, default=os.environ.get('PORT', '9000'), help='The HTTP port')
    parser.add_argument('--test', dest='test', action='store_true')
    parser.add_argument('--timezone', help="Set timezone of Sonos system", default='UTC')
    parser.add_argument("-v", "--verbose", help="Enable verbose logging", action="store_const", dest="loglevel", const=logging.INFO, default=logging.WARNING)
    parser.add_argument('-d', '--debug', help="Enable debug logging", action="store_const", dest="loglevel", const=logging.DEBUG)
    parser.add_argument('imap_host', metavar='IMAP_HOST', type=str, help='')
    parser.add_argument('imap_user', metavar='IMAP_USER', type=str, help='')
    parser.add_argument('imap_pass', metavar='IMAP_PASS', type=str, help='')
    parser.add_argument('imap_label', metavar='IMAP_LABEL', type=str, help='')

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel, format='%(relativeCreated)6d - %(threadName)-17s - %(name)s - %(levelname)s - %(message)s')

    sonos_alarm = SonosAlarm(args.port, args.timezone)

    http_server = HttpServer(args.port)
    mail_fetcher = MailFetcher(args.imap_host, args.imap_user, args.imap_pass, args.imap_label)
    mail_fetcher.add_new_mail_observer(sonos_alarm.alarm)

    logging.info("Starting server on port %s" % args.port)

    http_server_thread = threading.Thread(name="HTTPServerThread", target=http_server.serve_forever)
    http_server_thread.daemon = True
    http_server_thread.start()

    mail_fetcher_thread = threading.Thread(name="MailFetcherThread", target=mail_fetcher.fetch_forever)
    mail_fetcher_thread.daemon = True
    mail_fetcher_thread.start()

    if args.test:
        sonos_alarm.alarm()
        time.sleep(5)
    else:
        # Block until shutdown signal
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass

    mail_fetcher.stop()

    logging.info("Stopping server")
    http_server.shutdown()
