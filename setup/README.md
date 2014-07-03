ntfenervit dev environment
==========================

## Initial Setup

### Database Configuration
MySql server should be setup and running locally.  Following database needed:

| Key      | Value |
| -------- | ----- |
| Database | yellowpagedb |
| Username | enervit |
| Password | enervitdev |

* You can use `setup/sql/create_db.sql` to create the database


### Python Dependencies
After cloning this project, do the following to setup Python `virtualenv` and
install required package for the project:

```
cd ntfenervit
make devsetup
```

#### PIP Failure
PIP is notorious difficult package to install and it will often fail in Ubuntu.  If `make devsetup`
report error while installing PIP, try:

```
cd ntfenervit
sudo apt-get installl python-imaging
. pyenv/bin/activate
pip install --allow-external PIL --allow-unverified PIL PIL==1.1.7
```

If that does not work, you need to research how to install PIL in your platform.  Once PIP is correctly
installed, run `make devsetup` again to complete the installation.

#### Other Notes
1. For `MySQL-python`, you must make sure that `libmysqlclient-dev` is installed using `apt-get`



### Database Schema
Database schema needs to be initialized by doing:

```
cd ntfenervit
setup/initdb.sh
```

When prompted for superusers, answer `yes` and use the following:

| Key      | Value |
| -------- | ----- |
| Username | enervitdev |
| Email    | enervitdev@example.com |
| Password | devel02 |


### Launching Development Server
Dev server uses setting from `yellowPage/settings_dev.py`

```
cd ntfenervit
setup/devserver.sh
```

This will also launch a SMTP Logger server that will output any email sent to STDOUT


## Development Cli Environment

### Environment Variable Setup
To setup your bash to use the dev settings, do:
```
cd ntfenervit
. setup/devenv.sh
```

### Settings Override
To override the settings in *dev* mode, place a `settings_dev.json` file in the `yellowPage/` directory.
A sample file can be found at `setup/settings_dev.json`.  Do not add `yellowPage/settings_dev.json`
to repository as it is meant for developer specific customization.  In fact, this file is ignored in
`.gitignore`.

The `settings_dev.py` should be coded with default in place so that `settings_dev.json` is not needed.
