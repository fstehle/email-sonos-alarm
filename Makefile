venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv --python=python2.7
	venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

build:
	docker build -t fstehle/email-sonos-alarm .

build-rpi:
	docker build -f Dockerfile.rpi -t fstehle/rpi-email-sonos-alarm .
