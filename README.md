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

```
export IMAP_HOST="imap.gmail.com"
export IMAP_USER="mail.example.com"
export IMAP_PASS="secret"
export IMAP_ALARM_LABEL="some-label"
docker run --rm -p 9001:80 fstehle/email-sonos-alarm -v --port 9001 $IMAP_HOST $IMAP_USER $IMAP_PASS $IMAP_ALARM_LABEL
```

## Usage on a Raspberry Pi / ARMv7 with docker:

```
export IMAP_HOST="imap.gmail.com"
export IMAP_USER="mail.example.com"
export IMAP_PASS="secret"
export IMAP_ALARM_LABEL="some-label"
docker run --rm -p 9001:80 fstehle/rpi-email-sonos-alarm -v --port 9001 $IMAP_HOST $IMAP_USER $IMAP_PASS $IMAP_ALARM_LABEL
```

