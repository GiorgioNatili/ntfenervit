# ===========================================================
# Author:   Marcos Lin
# Created:	2 July 2014
#
# Makefile used to bootstrap ntfenervit django app
#
# ===========================================================

PYENV         = venv
PIP           = $(PYENV)/bin/pip
PYLIB_REQ     = requirements.txt
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


$(PYENV)/$(PYLIB_REQ) : $(PYLIB_REQ)
	@for pipdep in `cat $(PYLIB_REQ)`; \
	do \
		echo "### Installing $$pipdep"; \
		$(PIP) install $$pipdep; \
	done
	@cp -a $(PYLIB_REQ) $@


# ------------------
# MAIN TARGETS	
virtualenv : $(PIP) $(PYENV)/$(PYLIB_REQ)

setup : virtualenv

devsetup : setup
	@$(PIP) install -r $(SETUP)/dev_requirements.txt

# ------------------
# DEFINE PHONY TARGET: Basically all targets
.PHONY : \
	man virtualenv setup setup_lib

