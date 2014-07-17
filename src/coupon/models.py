import datetime
from django.contrib.auth.models import User
from django.db import models
from campaigns.models import Event
# Create your models here.


class CouponSet(models.Model):
    class Meta:
        verbose_name = "Pacchetto Coupon"
        verbose_name_plural = "Pacchetti Coupon"
    event = models.ForeignKey('campaigns.Event', blank=False, null=False, verbose_name="Evento")
    size = models.PositiveIntegerField(null=False, verbose_name="Numero coupons")
    owner = models.ForeignKey(User)
    max_date = models.DateField(blank=False, null=False)


    def __repr__(self):
        return 'SerieCoupon_%d__Evento_%d' % (self.id, self.event.id)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()


class Coupon(models.Model):
    '''
    The coupons will have a formatting like ENERVITXXXXXZZZYYYY
    where XXX is the progressive number associated with an event,
    ZZZ is the progressive number of the coupon and
    YYYY the current year.
    '''

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupon"

    coupon_bulk = models.ForeignKey('coupon.CouponSet', null=False, related_name='coupons')
    assigned_to = models.ForeignKey('contacts.Contact', null=True)
    used = models.BooleanField(verbose_name="Consumato", default=False)

    def is_valid(self, event_id):
        res = not self.used and event_id == self.coupon_bulk.event.id and self.coupon_bulk.max_date > datetime.date.today()
        return res

    def __repr__(self):
        year = self.coupon_bulk.event.date.year
        if self.id:
            return 'ENERVIT%d%05d%d' % (self.coupon_bulk.event.id, self.id, year)
        else:
            return 'ENERVIT%d%d' % (self.coupon_bulk.event.id, year)

    def __str__(self):
        return self.__repr__()

