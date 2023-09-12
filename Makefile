.PHONY: docs

venv = venv
bin = ${venv}/bin/
pysources = src/ test_project/ tests/

build:
	${bin}python -m build

check:
	${bin}ruff check ${pysources}
	${bin}black --check --diff ${pysources}
	${bin}mypy ${pysources}
	make migrations-check

docs:
	${bin}mkdocs build

docs-serve:
	${bin}mkdocs serve

docs-deploy:
	${bin}mkdocs gh-deploy

install: install-python

venv:
	python3 -m venv ${venv}

install-python: venv
	${bin}pip install -U pip wheel
	${bin}pip install -U build
	${bin}pip install -r requirements.txt
	./tools/install_django.sh ${bin}pip

format:
	${bin}ruff check --fix ${pysources}
	${bin}black ${pysources}

migrations:
	${bin}python -m tools.makemigrations

migrations-check:
	${bin}python -m tools.makemigrations --check

publish:
	${bin}twine upload dist/*

test:
	${bin}pytest
