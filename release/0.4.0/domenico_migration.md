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
*create users ITS for missing ones: Bosio, Marangi, Piovan
*its_districtmanager based on districtmanager

    python setup/release/20140811/populate_its.py
    
*consultant based on trainer

    python setup/release/20140811/populate_consultant.py
    
*then apply the following migration to remove old fields
    
    python src/manage.py migrate campaigns 0005 #this will remove unused fields
  
