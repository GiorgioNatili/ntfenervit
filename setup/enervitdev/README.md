enervitdev user
===============

`enervitdev` user has been setup in the test server to aid with development.  The primary objective of this
user is:

1. Allow for read-only access to the `/var/www` directory
2. Access to `mysql` restricted to `yellowpagedev` database
3. Deployment to `/var/www/test` directory

## Initial Setup

Connect to the test server using the following command:

```
ssh -p 20060 enervitdev@212.71.255.201
```

It will prompt for password for `enervitdev` which is provided to you separately.  Ideally, you use connect using
ssh-key, which you can add your public key to `.ssh/authorized_keys`.

## Deployment to Test

Once all code has been commit and merged into the master branch, do the following:

```
cd dev/ntfenervit
git pull
setup/deploy_test.sh
```

This will copy needed files from `src` to `dist_test`, with test specific files from the `conf/dist_test/` directory.
As `/var/www/test` is a symlink to `dist_test`, all subsequent work should take place in `/var/www/test`:

```
cd /var/www/test
manage.py ...
```

Create `whoosh_index` if not exists:

```
cd /var/www/test/yellowPage
mkdir whoosh_index
sudo chown www-data:www-data whoosh_index
```

After code and db deployment is completed, you must update Whoosh index and restart webserver by doing:

```
cd /var/www/test
sudo -u www-data DJANGO_SETTINGS_MODULE=yellowPage.settings_test ./manage.py update_index --remove
sudo service apache2 restart
```

**Notes**:

1. There is only one webserver for both prod and test.  As result, it is alway better to restart the server
only after business hours.  If you must do it doing the day, make sure to communicate with the user.  Normally,
the server restart takes only a few seconds.
2. NEVER change any source code directly in `/var/www/test` as any change will be overwritten by `deploy_test.sh`
3. You will see that `settings.py` is missing and replaced by `settings_test.py`.  This is intentional and any changes
to `settings_test.py` should be made in the project file `conf/dist_test/settings_test.py`.

## Reference

### Command used to setup enervitdev

```
# Command used to create user
useradd --gid users --groups adm,users,sudo --create-home --shell /bin/bash enervitdev

# Set password
passwd enervitdev

# Create user in mysql
create user 'enervitdev'@localhost identified by 'devel02';
grant all on yellowpagedev.* to 'enervitdev'@localhost;

# Add following to $HOME/.my.cnf
[client]
user=enervitdev
password=devel02

# Created github account
username: enervitdev
password: <<same as linux>>

# Add following to ~/.bash_profile
# Source .bashrc
if [ -e "${HOME}/.bashrc" ] ; then
  . "${HOME}/.bashrc"
fi

# Source .bashrc
test_profile="${HOME}/dev/ntfenervit/setup/enervitdev/test_profile.sh"
if [ -e "$test_profile" ]; then
  . "$test_profile"
fi

# Generate SSH key, no passphrase
# keyname: id_rsa_github
cd ~/.ssh/
ssh-keygen -t rsa -C "enervitdev@zc7.net"

# Clone repo
cd ~/dev/
git clone git@github.com:GiorgioNatili/ntfenervit.git

```
