pipenv := pipenv

installdeps:
	pip install .[dev]


check: test lint
lint: check-doc flake8

test: test-molecule

remote_python_version ?=
test-molecule:
	cd tests && REMOTE_PYTHON_VERSION=$(remote_python_version) ./molecule.sh


doc: README.md

check-doc:
	meta/gen_readme.py meta/README.md.j2 >.README.md.tmp
	diff -u README.md .README.md.tmp
	$(RM) .README.md.tmp

README.md: meta/README.md.j2 meta/gen_readme.py $(shell find ansible -type f -name '*.py')
	meta/gen_readme.py $< >.README.md.tmp
	mv -vf .README.md.tmp $@


sdist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

publish_repository ?= testpypi
publish: sdist wheel
	twine upload --repository $(publish_repository) dist/*

# Do not add to devdependencies because different platforms install
# different packages
publish-installdeps:
	pip install twine wheel


# Formatter and Linter ###############

flake8:
	flake8 --version
	flake8 .

# black

black:
	black .

# isort

isort:
	isort -rc .
