# ===========================================================
# Author:   Marcos Lin
# Created:	2 July 2014
#
# Makefile used to bootstrap ntfenervit django app
#
# ===========================================================

PYENV         = venv
PIP           = $(PYENV)/bin/pip
SETUP         = setup

# ------------------
# USAGE: First target called if no target specified
man :
	@cat $(SETUP)/readme.make

# ------------------
# Define file needed
$(PIP) :
ifeq ($(shell which virtualenv),)
	$(error virtualenv command needed to be installed.)
endif
ifeq ($(shell which mysql),)
	$(error mysql command needed to be installed.)
endif
	@virtualenv $(PYENV)


$(PYENV)/requirements.txt : requirements.txt
	@for pipdep in `cat $^`; \
	do \
		echo "### Installing $$pipdep"; \
		$(PIP) install $$pipdep; \
	done
	@cp -a $^ $@


$(PYENV)/dev_requirements.txt : setup/dev_requirements.txt
	@for pipdep in `cat $^`; \
	do \
		echo "### Installing $$pipdep"; \
		$(PIP) install $$pipdep; \
	done
	@cp -a $^ $@


# ------------------
# MAIN TARGETS	
virtualenv : $(PIP) $(PYENV)/requirements.txt

setup : virtualenv

devsetup : setup $(PYENV)/dev_requirements.txt

# ------------------
# DEFINE PHONY TARGET: Basically all targets
.PHONY : \
	man virtualenv setup setup_lib

