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
    
## To drop coupon_* tables and do syncdb again (branch coupon_CR_1)
#Added a field max_date DateField
 
#Modified the field its_user into owner (changed the FK to User)

## To add FK to coupons in EventSignup table

    coupon = models.ForeignKey('coupon.Coupon', null=True)
    
    ALTER TABLE campaigns_eventsignup ADD COLUMN `coupon_id` integer
    CREATE INDEX `campaigns_eventsignup_606a82fc` ON `campaigns_eventsignup` (`coupon_id`);
