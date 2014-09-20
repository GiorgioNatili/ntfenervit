Note for Production Migration
=============================

## New package requirement

    pip install python-Levenshtein
    
## Contact migration for company.company_code, company.type, company.name (not unique)

*schema migration

    python src/manage.py migrate contacts 0003
    python src/manage.py migrate contacts 0004
    python src/manage.py migrate contacts 0005
    
## Campaigns migration for change length of point of sale code

*schema migration

    python src/manage.py migrate campaigns 0003
    
    