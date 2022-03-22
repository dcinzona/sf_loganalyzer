update-deps:
	pip-compile --upgrade --allow-unsafe requirements/prod.in
	pip-compile --upgrade --allow-unsafe requirements/dev.in

dev-install:
	python -m pip install --upgrade pip pip-tools setuptools
	pip-sync requirements/*.txt
	python -m pip install -e .

coverage:
	pytest --cov --cov-report=html
	open htmlcov/index.html

.FORCE: