import logging
import socket

import time

import soco
from soco.snapshot import Snapshot

ALARM = "Sunday_Church_Ambiance-SoundBible.com-974744686.mp3"
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
        zones = self.get_zones()
        local_ip = self.get_local_ip(iter(zones).next())

        for zone in zones:
            zone.snap = Snapshot(zone)
            zone.snap.snapshot()
            logging.info('found zone')
            logging.info("%s, %s, %s" % (zone.snap.volume, zone.is_coordinator,  zone.player_name))

        coordinators = [zone for zone in zones if zone.is_coordinator]

        for zone_c in coordinators:
            trans_state = zone_c.get_current_transport_info()
            logging.info(zone_c.player_name, trans_state)
            if trans_state['current_transport_state'] == 'PLAYING':
                zone_c.pause()

        for zone in zones:
            zone.volume = 20

        for zone_c in coordinators:
            logging.info('Play alarm %s' % zone_c.player_name)
            zone_c.play_uri("http://%s:%i/%s" % (local_ip, self.port, ALARM), title="Alarm")

        time.sleep(14)
        for zone in zones:
            logging.info('restoring {}'.format(zone))
            zone.snap.restore(fade=True)


    @staticmethod
    def get_zones():
        zones = soco.discover(DISCOVER_TIMEOUT)
        if zones is None:
            raise RuntimeError("Cannot discover any Sonos Zones/Speakers")
        return zones

    @staticmethod
    def get_local_ip(zone):
        sonos_ip_address = zone.ip_address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((sonos_ip_address, 9))
            client = s.getsockname()[0]
        except socket.error:
            raise RuntimeError("Cannot detect local ip address")
        finally:
            del s
        return client
