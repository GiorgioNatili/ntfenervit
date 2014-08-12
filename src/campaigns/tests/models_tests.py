# -*- coding: utf-8 -*-

'''
Test for campaigns models
'''

from django.test import TestCase
from campaigns.models import EventType, ProductGroup

class EventModelTestCase(TestCase):
    fixtures = ['initial_data']

    def test01_EventType_get(self):
        '''Simple Initial Data Check'''
        et1 = EventType.objects.get(pk=1)
        self.assertEqual(et1.description, "SEMINARIO")

        et5 = EventType.objects.get(pk=5)
        self.assertEqual(et5.description, "PORTALE ENS")
        self.assertFalse(et5.selectable)

        # This test is to confirm assumption in the initial_data, also used in html_tests
        total_count = EventType.objects.count()
        self.assertEqual(total_count, 5, "Expected total EventType to be 5 but got %d" % total_count)

        selectable_count = EventType.objects.filter(selectable=True).count()
        self.assertEqual(selectable_count, 4, "Expected selectable entries to be 4 but got %d" % selectable_count)

    def test02_EventType_add(self):
        '''Test adding data and check for customer_to_sale_percent property'''
        data = {
            "description": "Test Q1J9I6N6nL",
            "contact_to_customer": 2,
            "customer_to_sale": 0.3,
            "selectable": True
        }

        et = EventType(**data)
        et.save()

        self.assertEqual(et.description, data["description"])
        self.assertEqual(et.customer_to_sale, data["customer_to_sale"])
        self.assertEqual(et.customer_to_sale_percent, data["customer_to_sale"] * 100)

class ProductGrouptTestCase(TestCase):
    fixtures = ['initial_data']

    def test01_ProductGroup_get(self):
        '''Simple Initial Data Check'''
        pg1 = ProductGroup.objects.get(pk=1)
        self.assertEqual(pg1.description, "10 SNACK")

        pg5 = ProductGroup.objects.get(pk=5)
        self.assertEqual(pg5.description, u'8 OMEGA 240, 6 MAQUI, 60 SNACK, 12 FROLLINI, VARIE PER 150€')

        # This test is to confirm assumption in the initial_data, also used in html_tests
        total_count = ProductGroup.objects.count()
        self.assertEqual(total_count, 5, "Expected total ProductGroup to be 5 but got %d" % total_count)


    def test02_ProductGroup_add(self):
        '''Test adding data and check for customer_to_sale_percent property'''
        data = {
            "description": "Test ProductGroup WvyXZVDism",
            "sell_in_alloc": 0.5,
            "sell_in_amount": 60
        }

        et = ProductGroup(**data)
        et.save()

        self.assertEqual(et.description, data["description"])
        self.assertEqual(et.sell_in_alloc, data["sell_in_alloc"])
        self.assertEqual(et.sell_in_alloc_percent, data["sell_in_alloc"] * 100)