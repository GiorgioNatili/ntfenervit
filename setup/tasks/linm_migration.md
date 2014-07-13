Note for Production Migration
=============================

## New `cabinet` app
* Added a new INSTALLED_APPS called cabinet
* Added new directory "/media/cabinet/" for uploaded files

## New `status` column in `survey_submission`
* sql used: `alter table survey_submission add column status smallint(6);`
