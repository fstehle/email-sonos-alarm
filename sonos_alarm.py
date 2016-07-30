import datetime
import logging

import soco
from soco.alarms import Alarm, get_alarms

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

        coordinators = [zone for zone in zones if zone.is_coordinator]

        alarms = soco.alarms.get_alarms()
        for alarm in alarms:
            if alarm.program_metadata == "EmailSonosAlarm" and alarm.enabled == False:
                alarm.remove()

        for zone_c in coordinators:
            logging.info('Enable alarm %s' % zone_c.player_name)
            alarm = Alarm(zone_c,
                          start_time=datetime.datetime.now() + datetime.timedelta(0, 10),
                          recurrence='ONCE',
                          program_metadata='EmailSonosAlarm',
                          include_linked_zones=True)
            alarm.save()

    @staticmethod
    def get_zones():
        zones = soco.discover(DISCOVER_TIMEOUT)
        if zones is None:
            raise RuntimeError("Cannot discover any Sonos Zones/Speakers")
        return zones
