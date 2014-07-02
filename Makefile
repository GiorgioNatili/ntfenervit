# ===========================================================
# Author:   Marcos Lin
# Created:	2 July 2014
#
# Makefile used to bootstrap ntfenervit django app
#
# ===========================================================

PYENV         = pyenv
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
ifeq ($(shell uname -s),Linux)
	@$(PIP) install --allow-external PIL --allow-unverified PIL -r $(PYLIB_REQ)
else
	@$(PIP) install -r $(PYLIB_REQ)
endif
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

