import logging
import threading

import re
from imaplib2 import imaplib2
from prometheus_client import Counter

pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')


class MailFetcher(object):
    def __init__(self, imap_host, imap_user, imap_pass, label, imap_port=None, use_ssl=True, imap_idle_timeout = 29 * 60):
        self.new_mail_observers = []
        if use_ssl:
            self.imap = imaplib2.IMAP4_SSL(imap_host, imap_port)
        else:
            self.imap = imaplib2.IMAP4(imap_host, imap_port)
        self.imap.login(imap_user, imap_pass)
        self.imap.select(label)
        self.imap_idle_timeout = imap_idle_timeout
        self.should_process_mailbox = True
        self.event = threading.Event()
        self.imap_idle_counter = Counter('imap_idle_commands_total', 'Number of IMAP IDLE commands sent to server')

    def add_new_mail_observer(self, observer):
        self.new_mail_observers.append(observer)

    def fetch_forever(self):
        while True:
            if self.should_process_mailbox:
                self.event.clear()
                self.process_mailbox()

            if self.event.isSet():
                return

            self.should_process_mailbox = False
            self.imap_idle_counter.inc()
            self.imap.idle(callback=self.imap_idle_callback, timeout=self.imap_idle_timeout)
            logging.info("Waiting for new messages")
            self.event.wait()

    def imap_idle_callback(self, args):
        if not self.event.isSet():
            self.should_process_mailbox = True
            self.event.set()

    def process_mailbox(self):
        logging.info("Checking for new messages")
        rv, data = self.imap.search(None, "ALL")
        if rv != 'OK' or data[0] is None or len(data[0]) == 0:
            logging.info("No messages found")
            return

        logging.info("Found some messages")
        for num in data[0].split():
            self.imap.store(num, '+FLAGS', '\\Deleted')
        self.imap.expunge()

        for observer in self.new_mail_observers:
            observer()

    def stop(self):
        self.event.set()
        self.imap.close()
        self.imap.logout()

    @staticmethod
    def parse_uid(data):
        match = pattern_uid.match(data)
        return match.group('uid')
