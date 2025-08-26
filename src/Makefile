# Variables
SHELL := /bin/bash
ENV_FILE=.env.docker
PYTHON=python3
PIP=pip
APP=src.main:app  

# Docker commands
up:
	docker compose --env-file $(ENV_FILE) up -d

down:
	docker compose --env-file $(ENV_FILE) down

logs:
	docker compose logs -f

# FastAPI commands
run:
	fastapi dev main.py

# Alembic migration commands
migrate:
	alembic upgrade head

makemigrations:
	alembic revision --autogenerate -m "migration"

downgrade:
	alembic downgrade -1

# Python package management
install:
	source venv/bin/activate && $(PIP) install -r requirements.txt

freeze:
	source venv/bin/activate && $(PIP) freeze > requirements.txt

# Init project
init:
	python3 -m venv venv
	source venv/bin/activate


