PYTHON ?= python
PIP ?= pip
MANAGE := $(PYTHON) manage.py

.PHONY: install run migrate makemigrations test docker-build docker-run docker-stop

install:
	$(PIP) install -r requirements.txt

run:
	DJANGO_DEBUG=1 $(MANAGE) runserver 0.0.0.0:8000

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

test:
	pytest -q

docker-build:
	docker build -t pesel-validator:latest .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env pesel-validator:latest

docker-stop:
	docker ps -q --filter ancestor=pesel-validator:latest | xargs -r docker stop
