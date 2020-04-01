pipenv := pipenv

installdeps:
	$(pipenv) install --dev

# Do this after updating dependencies in setup.cfg
updatedeps:
	$(pipenv) update


check: test check-doc

test: test-molecule

remote_python_version ?=
test-molecule:
	cd tests && REMOTE_PYTHON_VERSION=$(remote_python_version) $(pipenv) run ./molecule.sh


doc: README.md

check-doc:
	$(pipenv) run meta/gen_readme.py meta/README.md.j2 >.README.md.tmp
	diff -u README.md .README.md.tmp
	$(RM) .README.md.tmp

README.md: meta/README.md.j2 meta/gen_readme.py $(shell find ansible -type f -name '*.py')
	$(pipenv) run meta/gen_readme.py $< >.README.md.tmp
	mv -vf .README.md.tmp $@


sdist:
	python setup.py sdist

wheel:
	$(pipenv) run python setup.py bdist_wheel

publish_repository ?= testpypi
publish: sdist wheel
	$(pipenv) run twine upload --repository $(publish_repository) dist/*

# Do not add to devdependencies because different platforms install
# different packages
publish-installdeps:
	$(pipenv) run pip install twine wheel
