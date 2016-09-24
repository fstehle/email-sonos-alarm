# email-sonos-alarm

Create an alarm on your Sonos when a new mail is received

[![Build Status](https://circleci.com/gh/fstehle/email-sonos-alarm/tree/master.svg?style=shield)](https://circleci.com/gh/fstehle/email-sonos-alarm)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg "MIT License")](https://github.com/twbs/no-carrier/blob/master/LICENSE.txt)

## Usage on x86 machine:

Create your `Dockerfile` as follows:

```
pip install -r requirements.txt
python main.py IMAP_HOST IMAP_USER IMAP_PASS
```

## Usage on a x86 machine with Docker:

[![Docker Pulls](https://img.shields.io/docker/pulls/fstehle/email-sonos-alarm.svg?maxAge=2592000)]()

```
export IMAP_HOST="imap.gmail.com"
export IMAP_USER="mail.example.com"
export IMAP_PASS="secret"
export IMAP_ALARM_LABEL="some-label"
docker run --rm -p 9001:80 fstehle/email-sonos-alarm -v --port 9001 $IMAP_HOST $IMAP_USER $IMAP_PASS $IMAP_ALARM_LABEL
```

## Usage on a Raspberry Pi / ARMv7 with docker:

[![Docker RPi Pulls](https://img.shields.io/docker/pulls/fstehle/rpi-email-sonos-alarm.svg?maxAge=2592000)]()

```
export IMAP_HOST="imap.gmail.com"
export IMAP_USER="mail.example.com"
export IMAP_PASS="secret"
export IMAP_ALARM_LABEL="some-label"
docker run --rm -p 9001:80 fstehle/rpi-email-sonos-alarm -v --port 9001 $IMAP_HOST $IMAP_USER $IMAP_PASS $IMAP_ALARM_LABEL
```

## Create an alarm for your Pagerduty icidents on your Sonos

1. Add a valid email address under the `Contact Information` tab in your PagerDuty profile and make sure it receives emails for incidents in the `Notification Rules` tab.
2. Add a rule in your mail program / Gmail to sort the mail from PagerDuty into a specific IMAP folder / Gmail label.
3. Start the email-sonos-alarm program like described in the previous section



