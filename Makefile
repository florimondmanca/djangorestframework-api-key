venv = venv
bin = ${venv}/bin/
pysources = src/ test_project/ tests/

build:
	${python} setup.py sdist bdist_wheel
	${bin}twine check dist/*
	rm -r build

check:
	${bin}black --check --diff --target-version=py36 ${pysources}
	${bin}flake8 ${pysources}
	${bin}mypy ${pysources}
	${bin}isort --check --diff ${pysources}
	make migrations-check

docs:
	${bin}mkdocs build

docs-serve:
	${bin}mkdocs serve

docs-deploy:
	${bin}mkdocs gh-deploy

install:
	python3 -m venv ${venv}
	${bin}pip install -U pip wheel
	${bin}pip install -r requirements.txt

format:
	${bin}autoflake --in-place --recursive ${pysources}
	${bin}isort ${pysources}
	${bin}black --target-version=py36 ${pysources}

migrations:
	${bin}python -m tools.makemigrations

migrations-check:
	${bin}python -m tools.makemigrations --check

publish:
	${bin}twine upload dist/*

test:
	${bin}pytest
