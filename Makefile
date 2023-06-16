#* Variables
SHELL := /usr/bin/env bash
PYTHON := python3
PYTHONPATH := `pwd`

.PHONY: up
up: logs
	docker compose up --build --no-attach mongo --remove-orphans

.PHONY: upd
upd: logs
	docker compose up --build -d

.PHONY: down
down:
	docker compose down

.PHONY: clear-logs
clear-logs:
	sudo rm -rf logs/*

.PHONY: clear-db
clear-db:
	sudo rm -rf db

logs:
	mkdir logs

.PHONY: cleanstart
cleanstart: clear-logs clear-db up
