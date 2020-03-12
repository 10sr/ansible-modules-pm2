python ?= python3
pipenv := pipenv

sdist:
	$(python) setup.py sdist

wheel: installdeps
	$(pipenv) run python3 setup.py bdist_wheel

installdeps:
	$(pipenv) install --dev
