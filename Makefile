SHELL := /bin/bash

APP_NAME := sdxl-prompt-app
COMPOSE := docker compose
SERVICE := app
HOST ?= 127.0.0.1
APP_PORT ?= 5000
HEALTH_URL := http://$(HOST):$(APP_PORT)/api/health

.DEFAULT_GOAL := help

.PHONY: help setup start install check env build up dev ps logs shell restart down clean health open

help: ## Zeigt diese Hilfe
	@awk 'BEGIN {FS = ":.*##"; printf "\n%s\n\n", "$(APP_NAME)"; printf "Targets:\n"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Lokales Setup ausfuehren (.venv, Abhaengigkeiten, .env)
	@bash setup.sh

start: ## App lokal mit start.sh starten
	@bash start.sh

install: ## Python-Abhaengigkeiten in bestehende .venv installieren
	@. .venv/bin/activate && pip install -r requirements.txt

check: env ## Schneller Syntax- und Compose-Check
	@. .venv/bin/activate && python -m compileall -q app run.py
	@$(COMPOSE) config --quiet

env: ## .env aus .env.example anlegen, falls sie fehlt
	@test -f .env || cp .env.example .env

build: ## Container-Image bauen
	@$(COMPOSE) build $(SERVICE)

up: env ## Container im Hintergrund starten
	@APP_PORT=$(APP_PORT) $(COMPOSE) up -d $(SERVICE)

dev: env ## Container neu bauen und starten
	@APP_PORT=$(APP_PORT) $(COMPOSE) up -d --build $(SERVICE)

ps: ## Container-Status anzeigen
	@$(COMPOSE) ps

logs: ## App-Logs verfolgen
	@$(COMPOSE) logs -f $(SERVICE)

shell: ## Shell im laufenden App-Container oeffnen
	@$(COMPOSE) exec $(SERVICE) sh

restart: ## App-Container neu starten
	@$(COMPOSE) restart $(SERVICE)

down: ## Container stoppen und Netzwerk entfernen
	@$(COMPOSE) down

clean: ## Gestoppte Container und Compose-Netzwerk entfernen
	@$(COMPOSE) down --remove-orphans

health: ## Healthcheck gegen die laufende App ausfuehren
	@curl -fsS $(HEALTH_URL)
	@printf "\n"

open: ## App-URL ausgeben
	@printf "%s\n" "http://$(HOST):$(APP_PORT)"
