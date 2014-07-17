from django.forms import ModelForm
from coupon.models import CouponSet

__author__ = 'dominik'


class CouponSetForm(ModelForm):
    class Meta:
        model = CouponSet