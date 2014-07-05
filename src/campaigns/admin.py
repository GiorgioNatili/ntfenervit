from django.contrib import admin
from campaigns.models import Event,EventSignup,EventPayment,Campaign,Survey,Newsletter,NewsletterTarget,NewsletterAttachment,NewsletterTemplate

class NewsletterTemplateAdmin(admin.ModelAdmin):
    pass


class SurveyAdmin(admin.ModelAdmin):
    pass


class NewsletterAttachmentInLine(admin.StackedInline):
    model = NewsletterAttachment
    max_num=10
    extra=0


class EventAdmin(admin.ModelAdmin):
   pass

class NewsletterAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    inlines = [NewsletterAttachmentInLine,]
    exclude = ['author']
    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()

class NewsletterTargetAdmin(admin.ModelAdmin):
    pass



class EventSignupAdmin(admin.ModelAdmin):
    pass

class EventPaymentAdmin(admin.ModelAdmin):
    pass

class CampaignAdmin(admin.ModelAdmin):
    pass

admin.site.register(NewsletterTemplate,NewsletterTemplateAdmin)
admin.site.register(Survey,SurveyAdmin)
admin.site.register(Newsletter,NewsletterAdmin)
admin.site.register(NewsletterTarget,NewsletterTargetAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventPayment,EventPaymentAdmin)
admin.site.register(EventSignup,EventSignupAdmin)
admin.site.register(Campaign,CampaignAdmin)


