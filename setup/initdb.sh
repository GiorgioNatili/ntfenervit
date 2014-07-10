#!/bin/bash

#
# Author:  Marcos Lin
# Date:    02 July 2014
#
# Initialize the database using django's syncdb command
# using the devenv.sh
#

# proj_dir is the parent directory of script directory
proj_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
source "$proj_dir/setup/devenv.sh"
manage_cmd="$proj_dir/src/manage.py"

# Setup the core database
$manage_cmd syncdb

# Setup migrate the other apps
$manage_cmd migrate contacts
$manage_cmd migrate campaigns
