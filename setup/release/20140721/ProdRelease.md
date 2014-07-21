Production Turnover
===================

### Delete the old migration data
This is needed only one time as older migration scripts where removed

```
delete from south_migrationhistory
```

### Start the migration

```
manage.py syncdb
manage.py migrate campaigns 0001 --fake
manage.py  migrate campaigns 0002
manage.py  migrate survey 0001 --fake
manage.py  migrate survey 0002
```
