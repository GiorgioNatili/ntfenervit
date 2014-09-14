Note for Production Migration
=============================

## Contact migration for company.company_code and company.type

*schema migration

    python src/manage.py migrate contacts 0003
    python src/manage.py migrate contacts 0004
    
## Campaigns migration for change length of point of sale code

*schema migration

    python src/manage.py migrate campaigns 0003
    
    