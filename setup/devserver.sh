#!/bin/bash

#
# Author:  Marcos Lin
# Date:    02 July 2014
#
# Start the local dev server by launching the `manage.py runserver` using python
# from the virtualenv and instruct it to use `yellowPage/settings_dev.py` file
#

# proj_dir is the parent directory of script directory
proj_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
pycmd="$proj_dir/pyenv/bin/python"

# Override the default settings.py file used
export DJANGO_SETTINGS_MODULE="yellowPage.settings_dev"
$pycmd manage.py runserver 8000
