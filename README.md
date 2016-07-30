# email-sonos-alarm

Alert on new emails in Sonos

## Usage on x86 machine:

Create your `Dockerfile` as follows:

```
pip install -r requirements.txt
python main.py IMAP_HOST IMAP_USER IMAP_PASS
```

## Usage on a x86 machine with Docker:

```
docker run -it fstehle/email-sonos-alarm IMAP_HOST IMAP_USER IMAP_PASS
```

## Usage on a Raspberry Pi / ARMv7 with docker:

```
docker run -it fstehle/rpiemail-sonos-alarm IMAP_HOST IMAP_USER IMAP_PASS
```

