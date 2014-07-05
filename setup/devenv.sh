
#
# Author:  Marcos Lin
# Date:    02 July 2014
#
# Activate the python virtualenv and point django to use dev setting
# NOTE: this script should be sourced and not executed.
#

proj_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Activate Python VirtualEnv
source $proj_dir/venv/bin/activate

# Set dev setting
export DJANGO_SETTINGS_MODULE="yellowPage.settings_dev"
