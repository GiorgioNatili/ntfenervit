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

#### PIL Failure
PIL is notorious difficult package to install and it will often fail in Ubuntu.  If `make devsetup`
report error while installing PIP, try:

```
sudo apt-get installl python-imaging
. venv/bin/activate
pip install --allow-external PIL --allow-unverified PIL PIL==1.1.7
```

If that does not work, you need to research how to install `PIL==1.1.7` in your platform.  Once PIL is correctly
installed, run `make devsetup` again to complete the installation.

#### Linux Notes
1. For `MySQL-python`, you must install `libmysqlclient-dev` using `apt-get`
2. For `lxml`, you must install `libxml2-dev libxslt1-dev` using `apt-get`


### Database Schema
Database schema needs to be initialized by doing:

```
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
setup/devserver.sh
```

This will also launch a SMTP Logger server that will output any email sent to STDOUT


## Development Cli Environment

<a name="devEnvironSetup"></a>
### Dev Environment Setup
DO NOT use the usual `venv/bin/activate` to activate the `virtualenv`.  Instead, do:

```
. setup/devenv.sh
```

### Settings Override
To override the settings in *dev* mode, place a `settings_dev.json` file in the `yellowPage/` directory.
A sample file can be found at `setup/settings_dev.json`.  Do not add `yellowPage/settings_dev.json`
to repository as it is meant for developer specific customization.  In fact, this file is ignored in
`.gitignore`.

The `settings_dev.py` should be coded with default in place so that `settings_dev.json` is not needed.

### Unit Testing
In order to run unit testing, you need to have your [Dev Environment Setup](#devEnvironSetup) and then:

```
manage.py test survey
```

All test file should follow the following pattern:

* `<<package>>/tests.py` or in `<<package>>/tests/__init__.py`
* All test script should end with `*_tests.py`
* All test fixtures should be coded in JSON and ends with `*_tests.json`
* All test sql should end with `*_tests.sql`


## Development Procedures

### Arcanist
[Arcanist](https://secure.phabricator.com/book/phabricator/article/arcanist/) is used for code submitting the code for
review and approval.  A quick development cycle on arcanist is:

1. Identify the Task you are working on in [Phabricator](http://projects.gnstudio.biz/project/board/16/), i.e., `T419`
1. Create a branch in `git` so all work are done in that branch
1. Commit changes to the branch as you see fit.  Be descriptive on what you are committing as each commit will show up
   as an entry on the code review page
1. Once completed, submit changes using `arc diff` to create a [Differential Revision](http://projects.gnstudio.biz/D24)
1. Complete the process, merge changes to master and delete the branch, using `arc land` command

Here are the steps, assuming that we are working on `T419` task:

```
# Create and checkout a new branch
git checkout -b T419

# Add and commit as you see fit
git commit ...

# The first push of new needs `-u` option to create a tracking branch
# Following push can be simply done using `git push`
git push -u origin T419

# git cherry command to show commit in branch since master
git cherry -v master
+ d5cd505a498c9aaa3df5e0115c6075dfb14b9b3d Sort event by Event.date ascending for frontend main page
...

# Tell arc to pick up commit starting from the one prior to first commit in branch
arc diff d5cd505a498c9aaa3df5e0115c6075dfb14b9b3d^

# When approved, do
arc land

# arc land command will delete the local branch, so you must delete the remote one
git push origin :T419


```
