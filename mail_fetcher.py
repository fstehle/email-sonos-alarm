import logging
import threading

import re
from imaplib2 import imaplib2
from prometheus_client import Counter

pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')


class MailFetcher(object):
    def __init__(self, imap_host, imap_user, imap_pass, label, imap_port=None, use_ssl=True, imap_idle_timeout = 29 * 60):
        self.stop = False
        self.new_mail_observers = []
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.imap_user = imap_user
        self.imap_pass = imap_pass
        self.label = label
        self.use_ssl = use_ssl
        self.imap_idle_timeout = imap_idle_timeout
        self.should_process_mailbox = True
        self.event = threading.Event()
        self.imap_idle_counter = Counter('imap_idle_commands_total', 'Number of IMAP IDLE commands sent to server')
        self.imap = None

    def imap_connect(self):
        if self.use_ssl:
            imap = imaplib2.IMAP4_SSL(self.imap_host, self.imap_port)
        else:
            imap = imaplib2.IMAP4(self.imap_host, self.imap_port)
        imap.login(self.imap_user, self.imap_pass)
        imap.select(self.label)
        return imap

    def add_new_mail_observer(self, observer):
        self.new_mail_observers.append(observer)

    def fetch_forever(self):
        while not self.stop:
            self.event.clear()

            while self.imap is None:
                try:
                    self.imap = self.imap_connect()
                except (imaplib2.IMAP4.abort, imaplib2.IMAP4_SSL.abort, imaplib2.IMAP4.error) as e:
                    logging.error("There was an error in the imap connection: " + str(e))
                    time.sleep(10)

            if self.should_process_mailbox:
                try:
                    self.process_mailbox()
                except (imaplib2.IMAP4.abort, imaplib2.IMAP4_SSL.abort, imaplib2.IMAP4.error) as e:
                    logging.error("There was an error in the mailbox processing: " + str(e))
                    self.imap = None
                    continue

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

        self.notify_observers()


    def notify_observers(self, retries = 10, delay = 10):
        try:
            for observer in self.new_mail_observers:
                observer()
        except:
            time.sleep(delay)
            if retries == 0:
                raise
            self.notify_observers(retries - 1, delay)

    def stop(self):
        self.stop = true
        self.event.set()
        self.imap.close()
        self.imap.logout()

    @staticmethod
    def parse_uid(data):
        match = pattern_uid.match(data)
        return match.group('uid')
