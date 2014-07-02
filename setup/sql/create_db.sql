drop database if exists yellowpagedb;
# drop user 'enervit'@localhost;

create database yellowpagedb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
create user 'enervit'@localhost identified by 'enervitdev';
grant all on yellowpagedb.* to 'enervit'@localhost;
