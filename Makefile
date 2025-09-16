# Variables
SHELL := /bin/bash
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
ACTIVATE := source $(VENV)/bin/activate
APP := src.main:app  

run:
	$(ACTIVATE) && PYTHONPATH=.. uvicorn $(APP) --reload --host 0.0.0.0 --port 8000

install:
	$(ACTIVATE) && $(PIP) install --pre --timeout 120 --retries 10 -r requirements.txt

freeze:
	$(ACTIVATE) && $(PIP) freeze > requirements.txt

init:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE)
	$(MAKE) install

