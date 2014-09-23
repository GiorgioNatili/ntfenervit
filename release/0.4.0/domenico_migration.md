Note for Production Migration
=============================

## Contact migration for contact.type field

*schema migration

    python src/manage.py migrate contacts 0001 --fake
    python src/manage.py migrate contacts
    
## Campaigns app migration for several added fields in Event and EventType

*schema migration

    python src/manage.py migrate campaigns 0003
    python src/manage.py migrate campaigns 0004

## IMPORTANT: to plan a task for populate new Event fields based on old ones:
*This is needed for historical data. It can be done anytime.
*Contact the developer if this operation is requested in the future.

*create usersITS for missing ones: Bosio, Marangi, Piovan

*its_districtmanager based on old field 'districtmanager'
    
    python setup/release/20140811/populate_its.py
    
*consultant based on old field 'trainer'

    python setup/release/20140811/populate_consultant.py
    
*old field can be removed from code, then to create migration to apply
