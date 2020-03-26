python ?= python3
pipenv := pipenv

sdist:
	$(python) setup.py sdist

wheel:
	$(pipenv) run python setup.py bdist_wheel

installdeps:
	$(pipenv) install --dev

# Do this after updating dependencies in setup.cfg
updatedeps:
	$(pipenv) update


check: test

test: test-molecule

test-molecule:
	cd tests && $(pipenv) run ./molecule.sh


doc: README.md

README.md: meta/README.md.j2 $(shell find ansible -type f -name '*.py')
	$(pipenv) run meta/gen_readme.py $< >$@
