update-deps:
	pip-compile --upgrade --allow-unsafe requirements/prod.in
	pip-compile --upgrade --allow-unsafe requirements/dev.in

dev-install:
	pip install --upgrade pip-tools
	pip-sync requirements/*.txt
	pip install -e .

coverage:
	pytest --cov --cov-report=html
	open htmlcov/index.html

.FORCE: