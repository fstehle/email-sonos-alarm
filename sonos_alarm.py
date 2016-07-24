import logging
import socket

import soco

ALARM = "home_phone_ringing_soundbible.com-476855293.mp3"
DISCOVER_TIMEOUT = 60


class SonosAlarm(object):
    def __init__(self, port):
        self.port = port
        self.configure_logging(logging.getLogger().level)

    def configure_logging(self, level):
        logging.getLogger("requests").setLevel(logging.WARN)
        soco_logger = logging.getLogger("soco")
        if level == logging.DEBUG:
            soco_logger.setLevel(logging.INFO)
        else:
            soco_logger.setLevel(logging.WARN)

    def alarm(self):
        logging.info('Trigger alarm in Sonos')
        self.get_coordinator().play_uri("http://%s:%i/%s" % (self.get_local_ip(), self.port, ALARM), title="Alarm")

    @staticmethod
    def get_coordinator():
        zones = soco.discover(DISCOVER_TIMEOUT)
        if zones is None:
            raise RuntimeError("Cannot discover any Sonos Zones/Speakers")

        return zones.pop().group.coordinator

    @staticmethod
    def get_local_ip():
        sonos_ip_address = SonosAlarm.get_coordinator().ip_address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((sonos_ip_address, 9))
            client = s.getsockname()[0]
        except socket.error:
            raise RuntimeError("Cannot detect local ip address")
        finally:
            del s
        return client
