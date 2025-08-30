# Variables
SHELL := /bin/bash
ENV_FILE=.env.docker
PYTHON=python3
PIP=pip
APP=src.main:app  

# FastAPI commands
run:
	fastapi dev main.py



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


