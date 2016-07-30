venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv --python=python2.7
	venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

test: | venv/bin/activate
	venv/bin/nosetests tests

build:
	docker build -t fstehle/email-sonos-alarm .

build-rpi:
	docker build -f Dockerfile.rpi -t fstehle/rpi-email-sonos-alarm .

push: build
	docker push fstehle/email-sonos-alarm

push-rpi: build-rpi
	docker push fstehle/rpi-email-sonos-alarm
