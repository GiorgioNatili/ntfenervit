Note for Production Migration
=============================

## New settings variable
GOOGLE_MAP_API_KEY = 'AIzaSyDvwBg4JHzHXh4DISNEtFJwhYaMX0jv2ic'


## New package requirement

    pip install python-Levenshtein
    
## Contact migration for company.company_code, company.type, company.name (not unique)

*schema migration

    python src/manage.py migrate contacts
    
## Campaigns migration for change length of point of sale code

*schema migration

    python src/manage.py migrate campaigns
    
    