# drop database if exists yellowpagedb;
# drop user 'enervit'@localhost;

create database if not exists yellowpagedb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
create user 'enervit'@localhost identified by 'enervitdev';
grant all on yellowpagedb.* to 'enervit'@localhost;

# Following needed for unit test
GRANT CREATE, DROP ON *.* TO 'enervit'@localhost;
