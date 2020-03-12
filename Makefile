python ?= python3
pipenv := pipenv

sdist:
	$(python) setup.py sdist


installdeps:
	$(pipenv) install --dev
