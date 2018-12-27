MODULES=chunkedimage

all:	fast

fast:	lint mypy test docs-html

lint:   lint-non-init lint-init

lint-non-init:
	flake8 --ignore 'E252, E301, I201, E302, E305, E401, W503, E731, F811' --exclude='*__init__.py' $(MODULES)

lint-init:
	flake8 --ignore 'E252, E301, E302, E305, E401, F401, W503, E731, F811' --filename='*__init__.py' $(MODULES)

test:
	pytest -v -n 8 --cov chunkedimage

mypy:
	mypy --ignore-missing-imports $(MODULES)