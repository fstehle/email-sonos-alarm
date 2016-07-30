#!/usr/bin/env python
import smtplib
import threading
import unittest
from email.mime.text import MIMEText

import localmail
from mail_fetcher import MailFetcher
from mock import Mock

MAILBOX = "test@example.com"
IMAP_HOST = "localhost"
IMAP_PORT = 2143
IMAP_USER = "test@example.com"
IMAP_PASS = "xxx"
IMAP_LABEL = "INBOX"
IMAP_USE_SSL = False
SMTP_PORT = 2025
IMAP_IDLE_TIMEOUT = 1


class TestMailFetcher(unittest.TestCase):
    mail_fetcher = None
    imap_server_thread = None
    mail_observer_called_event = None
    mail_observer_mock = None

    @classmethod
    def setUpClass(cls):
        cls.imap_server_thread = threading.Thread(target=localmail.run, args=(SMTP_PORT, IMAP_PORT))
        cls.imap_server_thread.start()

        cls.mail_observer_called_event = threading.Event()
        cls.mail_observer_mock = Mock(side_effect=lambda *args, **kwargs: cls.mail_observer_called_event.set())

    @classmethod
    def tearDownClass(cls):
        cls.mail_fetcher.stop()
        localmail.shutdown_thread(cls.imap_server_thread)

    @classmethod
    def start_mail_fetcher(cls):
        cls.mail_fetcher = MailFetcher(IMAP_HOST, IMAP_USER, IMAP_PASS, IMAP_LABEL, IMAP_PORT, IMAP_USE_SSL,
                                       IMAP_IDLE_TIMEOUT)
        cls.mail_fetcher.add_new_mail_observer(cls.mail_observer_mock)

        mail_fetcher_thread = threading.Thread(name="MailFetcherThread", target=cls.mail_fetcher.fetch_forever)
        mail_fetcher_thread.daemon = True
        mail_fetcher_thread.start()

    @classmethod
    def send_mail(self, from_, to, subject, body):
        try:
            smtp = smtplib.SMTP('localhost', SMTP_PORT)
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = from_
            msg['To'] = to
            smtp.sendmail(from_, [to], msg.as_string())
        except smtplib.SMTPException:
            raise Exception("Error: unable to send email")

    def test_new_mail_observer_invoked(self):

        self.assertFalse(self.mail_observer_mock.called)

        self.send_mail(MAILBOX, MAILBOX, 'Test mail', "This is a test e-mail message")
        self.start_mail_fetcher()

        self.mail_observer_called_event.wait(10)
        self.assertEqual(self.mail_observer_mock.call_count, 1,
                         "mail observer should have been called once, called {times} times!".format(
                                 times=self.mail_observer_mock.call_count))

        self.mail_observer_called_event.clear()
        self.mail_observer_mock.reset_mock()
        self.send_mail(MAILBOX, MAILBOX, 'Test mail', "This is a test e-mail message")

        self.mail_observer_called_event.wait(10)
        self.assertEqual(self.mail_observer_mock.call_count, 1,
                         "mail observer should have been called once, called {times} times!".format(
                             times=self.mail_observer_mock.call_count))


if __name__ == '__main__':
    unittest.main()
