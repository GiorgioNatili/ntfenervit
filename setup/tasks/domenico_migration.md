Note for Production Migration
=============================

## New `coupon` app
* Added a new INSTALLED_APPS called coupon

## Added a settings for Survey

    #SURVEY app
    #this setting serve to find the threshold date
    # for a survey to be considered as abandoned
    #It's the maximum number of days passed since
    # last access to the survey to be considered
    # as Active (in corso)
    SURVEY_ACTIVE_DAYS = 15
