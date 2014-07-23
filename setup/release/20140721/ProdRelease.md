Production Turnover
===================

### Delete the old migration data
This is needed only one time as older migration scripts were removed

```
delete from south_migrationhistory;
```

### Turn over the code

```
cd ~enervitdev/dev/ntfenervit
git pull
setup/deploy_prod.sh -w
sudo chown -R www-data:www-data /var/www/yellowpage/
```

### Start the migration

```
cd /var/www/yellowpage/

manage.py syncdb
manage.py migrate campaigns 0001 --fake
manage.py migrate campaigns 0002
manage.py migrate survey 0001 --fake
manage.py migrate survey 0002
```

### Update Index

```
sudo -u www-data ./manage.py update_index
```

### Update Index

sudo -u www-data /var/www/yellowpage/manage.py update_index --remove

Production Users
================

Following users are created for post production release testing:

```
BACKEND USER:
user: enervitdev
mail: enervitdev@mochunk.com

FRONTEND USER:
user: gbianchi
mail:enervitdev@zc7.net
```
