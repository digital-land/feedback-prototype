init::
	python -m pip install --upgrade pip
	python -m pip install pip-tools
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt
	python -m pre_commit install
	npm install

frontend:
	npm install

black:
	black .

black-check:
	black --check .

flake8:
	flake8 .

isort:
	isort --profile black .

lint: black-check flake8

run:
	flask run

watch:
	npm run watch

test:
	python -m pytest

reqs:
	python -m piptools compile requirements/requirements.in
	python -m piptools compile requirements/dev-requirements.in

sync:
	 python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

upgrade-db:
	flask db upgrade

downgrade-db:
	flask db downgrade

data-load:
	flask data load

data-drop:
	flask data drop
