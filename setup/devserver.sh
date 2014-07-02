#!/bin/bash

#
# Author:  Marcos Lin
# Date:    02 July 2014
#
# Start the local dev server by launching the `manage.py runserver` using the devenv.sh
# Launch the smtplogger.py in the background
#

# proj_dir is the parent directory of script directory
proj_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
source "$proj_dir/setup/devenv.sh"

# Start the fake smtp server
echo "### Launching SMTP Logger..."
$proj_dir/setup/smtplogger.py &
smtp_pid=$!
echo "### SMTP Logger started with PID $smtp_pid"

# Kill the smtplogger process upon exit
cleanup ()
{
    echo "### Stopping SMTP Logger [$smtp_pid]..."
    kill $smtp_pid
    if [ $? -eq 0 ]; then
        echo "### SMTP Logger killed."
        exit 0
    else
        echo "### FAILED to kill SMTP Logger.  Check you system process"
        exit 1
    fi
}

trap cleanup SIGINT

# Start the webserver
manage.py runserver 8000
