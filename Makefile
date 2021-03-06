.PHONY: all install install-dev test qa

all:

install:
	pip3 install -r requirements/requirements.txt --no-binary :all:
	./setup.py install

install-dev:
	pip3 install -r requirements/requirements.txt --no-binary :all:
	pip3 install -r requirements/requirements-dev-1.txt --no-binary :all:
	pip3 install -r requirements/requirements-dev-2.txt --no-binary :all:
	pip3 install -r requirements/requirements-dev-3.txt --no-binary :all:
	./setup.py develop

test:
	python3 -m unittest -q

qa:
	coverage run -m unittest -q
	coverage report -m
	isort --check-only --diff --recursive .
	mypy .
	ossaudit \
		--file requirements/requirements.txt \
		--file requirements/requirements-dev-1.txt \
		--file requirements/requirements-dev-2.txt \
		--file requirements/requirements-dev-3.txt
	pycodestyle .
	pyflakes .
	pylint --output-format parseable setup.py pkrecv tests
	safety check --bare --cache
	yapf --diff --recursive .
