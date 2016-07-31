import datetime
import time
import logging

import pytz
import soco
from soco.alarms import Alarm, get_alarms

DISCOVER_TIMEOUT = 60


class SonosAlarm(object):
    def __init__(self, port, timezone):
        self.port = port
        self.configure_logging(logging.getLogger().level)
        self.timezone = pytz.timezone(timezone)

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

        coordinators = list([zone for zone in zones if zone.is_coordinator])

        for zone_c in coordinators:
            logging.info('Start alarm in zone %s' % zone_c.player_name)
            self.alarm_coordinator(zone_c)

    def alarm_coordinator(self, coordinator, delay=2, retries=10):
        logging.info('Try to create an alarm in zone %s, retries %i' % (coordinator.player_name, retries))
        alarm = Alarm(coordinator,
                      start_time=datetime.datetime.now(self.timezone) + datetime.timedelta(0, delay),
                      duration=datetime.time(0, 2, 0),
                      recurrence='ONCE',
                      program_metadata='EmailSonosAlarm',
                      include_linked_zones=True)
        alarm.save()

        time.sleep(delay + 2)
        soco.alarms.get_alarms(coordinator)

        alarm_enabled = alarm.enabled
        alarm.remove()

        if not alarm_enabled:
            logging.info('Alarm in zone %s was triggered' % coordinator.player_name)
        else:
            if retries == 0:
                logging.error('Could not trigger alarm in zone %s' % coordinator.player_name)
            else:
                self.alarm_coordinator(coordinator, delay ** 2, retries - 1)

    @staticmethod
    def get_zones():
        zones = soco.discover(DISCOVER_TIMEOUT)
        if zones is None:
            raise RuntimeError("Cannot discover any Sonos Zones/Speakers")
        return zones
