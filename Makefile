
PACKAGE_TARGETS := assembly.py automaton.py components mad.py \
	Makefile README.md requirements.txt utils

CTAGS := $(shell command -v ctags 2> /dev/null)
CTAGS-exists : ; @which ctags > /dev/null
PYTHON3-exists := $(shell command -v python3 2> /dev/null)
PIP-exists := $(shell command -v pip3 2> /dev/null)
VIRTUALENV-exists : ; @which virtualenv > /dev/null

check_python3:
ifndef PYTHON3-exists
	$(error "python3 is not available - please install it.")
endif

check_pip3:
ifndef PIP-exists
	$(error "pip3 is not available - please install it.")
endif

virtualenv: check_python3 check_pip3
	@echo Check if the software 'virtualenv' is installed.
	@echo [WARNING] Using 'pip' to install it in the user directory.
	hash virtualenv 2>/dev/null || pip install --user virtualenv

venv3: virtualenv venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || virtualenv --python=python3 venv
	venv/bin/pip install -r requirements.txt;
	touch venv/bin/activate

# This rule installs dependencies with pip in virtual environments (venv).
# `python3' and `python3-pip' have to be already installed. If `virtualenv'
# is not installed, this rule installs it with pip in the user directory.
# This rule also install EnOS dependencies if EnOS is here.
install_deps: venv3

# This rule installs dependencies in the user directory.
install_deps_user:
	pip install --user -r requirements.txt
	
remove_deps:
	-rm -rf venv

package: mad.tgz
mad.tgz: $(PACKAGE_TARGETS)
	tar -zcvf $@\
		--exclude "venv"\
		--exclude "__pycache__"\
		--exclude "*.swo"\
		--exclude "*.swp" $^

small_package: small_mad.tgz
small_mad.tgz: $(PACKAGE_TARGETS)
	tar -zcvf $@\
		--exclude "venv"\
		--exclude "__pycache__"\
		--exclude "*.swo"\
		--exclude "*.swp" $^

tags: CTAGS-exists
	# exuberant-ctags must be installed
#	ifndef CTAGS
#		$(error "'ctags' is not available, exuberant-ctags must be installed.")
#	endif
	ctags -R --fields=+l --languages=python --python-kinds=-iv \
		--exclude=venv

clean:
	-rm result_*.txt
	-rm result_*.html

