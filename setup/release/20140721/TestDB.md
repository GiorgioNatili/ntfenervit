Create a new Test DB with Production Data
=========================================

### Extract the insert statement from the production database

```
mysqldump --no-create-info --complete-insert yellowpagedb -r <<filename>>
```

### Create a brand new test db

```
drop database if exists yellowpage_local;
create database if not exists yellowpage_local DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

# drop user 'enervit_devuser'@localhost;
create user 'enervit_devuser'@localhost identified by 'v22ghIqnqH';
grant all on yellowpage_local.* to 'enervit_devuser'@localhost;

# Following needed for unit test
GRANT CREATE, DROP ON yellowpage_local.* TO 'enervit_devuser'@localhost;
```

### Create a yellowPage/settings_dev.json with:

```
{
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "yellowpage_local",
            "USER": "enervit_devuser",
            "PASSWORD": "v22ghIqnqH",
            "HOST": "",
            "PORT": ""
        }
    }
}
```

### Create needed tables
Temporarly remove all the migrations directory and do:


```
manage.py syncdb --no-initial-data
```


### Run the following sql to delete initial data populated by django

```
delete from auth_permission;
delete from auth_user;
delete from django_content_type;
delete from django_site;
```

### Load the sql file extrated from first step

```
mysql --database yellowpage_local < <<filename>>
```

### Change password

The password for existing users might not work anymore.  If you have any problem login in, you need to reset the
password by doing.

```
manage.py shell
>>> from django.contrib.auth.models import User
>>> u = User.objects.get(username='<<username>>')
>>> u.set_password('<<password>>')
>>> u.save()
```

