from django.contrib import admin
from contacts.models import Region, Province, Company, Division, SubDivision, Sector, Work, Payment, Visit, ChampionsDelivery, Contact, RankingConfiguration


class RegionAdmin(admin.ModelAdmin):
    pass


class ProvinceAdmin(admin.ModelAdmin):
    pass


class CompanyAdmin(admin.ModelAdmin):
    pass


class DivisionAdmin(admin.ModelAdmin):
    pass


class SubDivisionAdmin(admin.ModelAdmin):
    pass


class SectorAdmin(admin.ModelAdmin):
    pass


class WorkAdmin(admin.ModelAdmin):
    pass


class PaymentAdmin(admin.ModelAdmin):
    pass


class VisitAdmin(admin.ModelAdmin):
    pass


class ChampionsDeliveryAdmin(admin.ModelAdmin):
    pass


class ContactAdmin(admin.ModelAdmin):
    pass

class RankingConfigurationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Region, RegionAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Division, DivisionAdmin)
admin.site.register(SubDivision, SectorAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ChampionsDelivery, ChampionsDeliveryAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(RankingConfiguration,RankingConfigurationAdmin)
