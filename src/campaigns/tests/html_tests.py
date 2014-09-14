# -*- coding: utf-8 -*-

"""
run client tests
"""

import lxml.html
from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from campaigns.models import ProductGroup


class BaseHTMLTestCase(TestCase):
    """
    Base Test Class for HTML TestCases with GUI utilities
    """
    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    def _get_elem_from_url(self, url):
        """
        Private method to return a parsed element from url
        :param url: URL to retrieve HTML from
        :return: a parsed element
        """
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))
        doc = lxml.html.fromstring(resp.content)

        # self.assertTrue(doc, "Failed to parse '%s'.  HTML:\n%s" % (url, resp.content))
        self.assertTrue(doc, "Failed to parse '%s'" % url)
        return doc

    def _get_elements(self, element, selector):
        """
        Get a list of elements from a selector
        :param element: Parsed element
        :param selector: Optional selector to apply on element
        :return: list of parsed elements
        """
        result = []
        if isinstance(element, list):
            for elem in element:
                result.extend(elem.cssselect(selector))
        else:
            result.extend(element.cssselect(selector))
        return result


    def _get_list_from_element(self, element, selector=None, attr=None):
        """
        Private method to convert element to list of strings
        :param element: Parsed element
        :param selector: Optional selector to apply on element
        :param attr: Optional return given attribute instead of html.  Support for 'object.text' that
                     return elem.text property.
        :return: list of string
        """
        if selector:
            elem = self._get_elements(element, selector)
        else:
            elem = element

        if attr=="object.text":
            result = [x.text for x in elem]
        elif attr:
            result = [x.get(attr) for x in elem]
        else:
            result = [lxml.html.tostring(x) for x in elem]

        return result


class EventTypeHTMLTestCase(BaseHTMLTestCase):
    fixtures = ['initial_data', 'users_tests.json']

    def setUp(self):
        self.admin = User.objects.get(pk=1)
        self.is_logged_in = self.client.login(username=self.admin.username, password="devel02")
        self.eventType_id_Seminario = 1


    def test01_EventType_list(self):
        '''Check for EventType list view'''
        doc = self._get_elem_from_url("/admin/campaigns/eventtype/")

        # Make sure header is generated as expected
        headers = self._get_list_from_element(doc, selector="#dataTables > table > thead > tr > th > div", attr="object.text")
        expected_headers = ['Descrizione', 'Contatti Lordi', 'Contatti Netti', 'Selezionabile']
        self.assertEqual(headers, expected_headers)

        # Make sure number of row returned is as expected
        rows = self._get_elements(doc, selector="#dataTables > table > tbody > tr")
        self.assertEqual(len(rows), 5, "Expected EventType list to contain 5 entries but got %d" % len(rows))

        # Look for "PORTALE ENS" and "SEMINARIO" rows and check for the data
        for row in rows:
            cells = row.getchildren()
            title = cells[0].text
            if title == "SEMINARIO":
                row_text = self._get_list_from_element(row, attr="object.text")
                expected_row_text = ['SEMINARIO', '1', '20,0 %', u'Sì', None]
                self.assertEqual(row_text, expected_row_text)

    def test02_EventType_edit(self):
        '''Test Editing existing EventType'''
        url = "/admin/campaigns/eventtype/%d" % self.eventType_id_Seminario

        # Check initial data
        doc = self._get_elem_from_url(url)
        result = self._get_list_from_element(doc, "form#company_form > div > div.span6 > ul > li > input", attr="value")
        expected_result = ['SEMINARIO', None, '1.0', '0.2']
        self.assertEqual(result, expected_result)

        # Make sure update succeeds and redirect expected URL
        csrf_token=self._get_list_from_element(doc, "form#company_form > input[name='csrfmiddlewaretoken']", attr="value")
        self.assertEqual(len(csrf_token),1,"Expected to find csrfmiddlewaretoken")
        post_data = {
            "description": "SEMINARIO FfRPCZQZI7",
            "selectable": True,
            "contact_to_customer": "14.0",
            "customer_to_sale": "0.4",
            "csrfmiddlewaretoken": csrf_token[0]
        }

        resp = self.client.post(url, post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertRegexpMatches(resp.get("location"), r'\/admin\/campaigns\/eventtype$')

        # Check updated data
        doc = self._get_elem_from_url(url)
        result = self._get_list_from_element(doc, "form#company_form > div > div.span6 > ul > li > input", attr="value")
        expected_result = [post_data["description"], None, post_data["contact_to_customer"], post_data["customer_to_sale"]]
        self.assertEqual(result, expected_result)

    def test03_EventType_add(self):
        '''Test Adding a new EventType'''
        url = "/admin/campaigns/eventtype/add/"

        # Create post data with the csrf_token
        doc = self._get_elem_from_url(url)
        csrf_token=self._get_list_from_element(doc, "form#company_form > input[name='csrfmiddlewaretoken']", attr="value")
        self.assertEqual(len(csrf_token),1,"Expected to find csrfmiddlewaretoken")
        post_data = {
            "description": "TEST tIZc66b7LP",
            "selectable": False,
            "contact_to_customer": "66",
            "customer_to_sale": "0.7",
            "customer_to_sale_percent": "70,0 %",
            "csrfmiddlewaretoken": csrf_token[0]
        }

        # Make sure post works
        resp = self.client.post(url, post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertRegexpMatches(resp.get("location"), r'\/admin\/campaigns\/eventtype$')

        # Check that it has been added
        doc = self._get_elem_from_url("/admin/campaigns/eventtype/")

        # Make sure number of row returned is as expected
        rows = self._get_elements(doc, selector="#dataTables > table > tbody > tr")
        self.assertEqual(len(rows), 6, "Expected EventType list to contain 6 entries but got %d" % len(rows))

        # Look for "PORTALE ENS" and "SEMINARIO" rows and check for the data
        for row in rows:
            cells = row.getchildren()
            title = cells[0].text
            if title == post_data['description']:
                row_text = self._get_list_from_element(row, attr="object.text")
                expected_row_text = [post_data["description"], post_data["contact_to_customer"], post_data["customer_to_sale_percent"], 'No', None]
                self.assertEqual(row_text, expected_row_text)

    def test04_EventType_dropdown(self):
        '''Make sure EventType dropdown only shows selectable = True'''
        url = "/admin/campaigns/event/add/"
        doc = self._get_elem_from_url(url)

        result = self._get_list_from_element(doc, "form#event_form > div.row-fluid > div.span6 > ul > li > select[name='eventtype'] > option", attr="object.text")
        result_expected = ['---', 'SEMINARIO', 'ONE-TO-ONE', 'FORMAZIONE A PUNTO VENDITA', 'INFORMAZIONE MEDICA']
        self.assertItemsEqual(result, result_expected)


class ProductGroupHTMLTestCase(BaseHTMLTestCase):
    fixtures = ['initial_data', 'users_tests.json']

    def setUp(self):
        self.admin = User.objects.get(pk=1)
        self.is_logged_in = self.client.login(username=self.admin.username, password="devel02")
        self.eventType_id_Seminario = 1

    def test01_ProductGroup_list(self):
        '''Check for ProductGroup list view'''
        doc = self._get_elem_from_url("/admin/campaigns/productgroup/")

        # Make sure header is generated as expected
        headers = self._get_list_from_element(doc, selector="#dataTables > table > thead > tr > th > div", attr="object.text")
        expected_headers = ['Livello', 'Descrizione', 'Percentuale sell in', 'Valore sell in']
        self.assertEqual(headers, expected_headers)

        # Make sure number of row returned is as expected
        rows = self._get_elements(doc, selector="#dataTables > table > tbody > tr")
        self.assertEqual(len(rows), 5, "Expected ProductGroup list to contain 5 entries but got %d" % len(rows))

        # Look for first and last row and check for the data
        for row in rows:
            cells = row.getchildren()
            id = cells[0].text
            if id == "1":
                row_text = self._get_list_from_element(row, attr="object.text")
                expected_row_text = ['1', '10 SNACK', '30,0 %', '9,95 ', None]
                self.assertEqual(row_text, expected_row_text)
            elif id == "5":
                row_text = self._get_list_from_element(row, attr="object.text")
                expected_row_text = ['5', u'8 OMEGA 240, 6 MAQUI, 60 SNACK, 12 FROLLINI, VARIE PER 150€', '10,0 %', '698,30 ', None]
                self.assertEqual(row_text, expected_row_text)

    def test02_ProductGroup_edit(self):
        '''Test Editing existing ProductGroup'''
        url = "/admin/campaigns/productgroup/%d" % 1

        # Check initial data
        doc = self._get_elem_from_url(url)
        result = self._get_list_from_element(doc, "form#company_form > div > div.span6 > ul > li > input", attr="value")
        expected_result = ['10 SNACK', '0,3', '9,95']
        self.assertEqual(result, expected_result)

        # Make sure update succeeds and redirect expected URL
        csrf_token=self._get_list_from_element(doc, "form#company_form > input[name='csrfmiddlewaretoken']", attr="value")
        self.assertEqual(len(csrf_token),1,"Expected to find csrfmiddlewaretoken")
        post_data = {
            "description": "10 SNACK 2oVKaPEr0E",
            "sell_in_alloc": "0,22",
            "sell_in_amount": "330,0",
            "csrfmiddlewaretoken": csrf_token[0]
        }

        resp = self.client.post(url, post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertRegexpMatches(resp.get("location"), r'\/admin\/campaigns\/productgroup$')

        # Check updated data
        doc = self._get_elem_from_url(url)
        result = self._get_list_from_element(doc, "form#company_form > div > div.span6 > ul > li > input", attr="value")
        expected_result = [post_data["description"], post_data["sell_in_alloc"], post_data["sell_in_amount"]]
        self.assertEqual(result, expected_result)

    def test03_ProductGroup_add(self):
        '''Test Adding a new ProductGroup'''
        url = "/admin/campaigns/productgroup/add/"

        # Create post data with the csrf_token
        doc = self._get_elem_from_url(url)
        csrf_token=self._get_list_from_element(doc, "form#company_form > input[name='csrfmiddlewaretoken']", attr="value")
        self.assertEqual(len(csrf_token),1,"Expected to find csrfmiddlewaretoken")
        post_data = {
            "description": "TEST product group wT344FySHo",
            "sell_in_alloc": "0,33",
            "sell_in_amount": "440,00 ",
            "csrfmiddlewaretoken": csrf_token[0]
        }

        # Make sure post works
        resp = self.client.post(url, post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertRegexpMatches(resp.get("location"), r'\/admin\/campaigns\/productgroup$')

        # Check that it has been added
        doc = self._get_elem_from_url("/admin/campaigns/productgroup/")

        # Make sure number of row returned is as expected
        # Check that only 5 records are left
        self.assertEqual(ProductGroup.objects.all().count(), 6)
        rows = self._get_elements(doc, selector="#dataTables > table > tbody > tr")
        self.assertEqual(len(rows), 6, "Expected ProductGroup list to contain 6 entries but got %d" % len(rows))

        # Look for the row added and make sure it is there
        added_id = None
        for row in rows:
            cells = row.getchildren()
            title = cells[1].text
            if title == post_data['description']:
                added_id = cells[0].text
                row_text = self._get_list_from_element(row, attr="object.text")
                expected_row_text = [added_id, post_data["description"], '33,0 %', post_data["sell_in_amount"], None]
                self.assertEqual(row_text, expected_row_text)
        self.assertIsNotNone(added_id, "Expected the row to be added.")

        # Now delete it
        url = "/admin/campaigns/productgroup/%s" % added_id
        doc = self._get_elem_from_url(url)
        csrf_token=self._get_list_from_element(doc, "form#company_form > input[name='csrfmiddlewaretoken']", attr="value")
        self.assertEqual(len(csrf_token),1,"Expected to find csrfmiddlewaretoken")
        post_data = {
            "action": "delete",
            "csrfmiddlewaretoken": csrf_token[0]
        }

        resp = self.client.post(url, post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertRegexpMatches(resp.get("location"), r'\/admin\/campaigns\/productgroup$')

        # Check that only 5 records are left
        self.assertEqual(ProductGroup.objects.all().count(), 5)


class ITSReportHTMLTestCase(BaseHTMLTestCase):
    fixtures = ['initial_data', 'users_tests.json', 'contacts_tests.json', 'events_tests.json']

    def setUp(self):
        self.admin = User.objects.get(pk=1)
        self.is_logged_in = self.client.login(username=self.admin.username, password="devel02")
        self.year = 2014

    def test01_rpt_contacts(self):
        '''Testing Report: Stima Contatti Lordi'''
        url = "/admin/its/report/%s" % self.year
        doc = self._get_elem_from_url(url)

        result = self._get_list_from_element(doc, "#rpt-contacts > tbody > tr > td", attr="object.text")
        result_expected = [
            'SEMINARIO', '3', '204', '1,0', '204,0',
            'ONE-TO-ONE', '2', '122', '1,0', '122,0',
            'FORMAZIONE A PUNTO VENDITA', '1', '105', '3,0', '315,0',
            'INFORMAZIONE MEDICA', '1', '77', '8,0', '616,0',
            'TOTALE', '7', '508', u'\xa0', '1.257'
        ]

        self.assertEqual(result, result_expected)

    def test02_rpt_contacts(self):
        '''Testing Report: Sintesi Numero Consumatori'''
        url = "/admin/its/report/%s" % self.year
        doc = self._get_elem_from_url(url)

        result = self._get_list_from_element(doc, "#rpt-sales > tbody > tr > td", attr="object.text")
        result_expected = [
            'SEMINARIO', '204', '20,0%', '41',
            'ONE-TO-ONE', '122', '30,0%', '37',
            'FORMAZIONE A PUNTO VENDITA', '315', '30,0%', '95',
            'INFORMAZIONE MEDICA', '616', '40,0%', '246',
            'TOTALE', '1.257', u'\xa0', '418', '33,28%'
        ]
        self.assertEqual(result, result_expected)

    def test03_rpt_revenue(self):
        '''Testing Report: Stima Fatturati'''
        url = "/admin/its/report/%s" % self.year
        doc = self._get_elem_from_url(url)

        result = self._get_list_from_element(doc, "#rpt-revenue > tbody > tr > td", attr="object.text")
        result_expected = [
            '1', u'10 SNACK', '\n                                        ', '30,0%', u'9,95 €', u'1.249 €',
            '2', u'1 OMEGA 120, 6 SNACK, 2 FROLLINI', '20,0%', u'38,57 €', u'3.227 €',
            '3', u'2 OMEGA 3 DA 120 CPS, 12 SNACK, 4 FROLLINI, VARIE PER 20€', '20,0%', u'87,14 €', u'7.290 €',
            '4', u'6 OMEGA 240, 4 MAQUI, 30 SNACK, 8 FROLLINI, VARIE PER 100€', '20,0%', u'487,25 €', u'40.763 €',
            '5', u'8 OMEGA 240, 6 MAQUI, 60 SNACK, 12 FROLLINI, VARIE PER 150€', '10,0%', u'698,30 €', u'29.210 €',
            'TOTALE FATTURATO', u'81.739 €']

        self.assertEqual(result, result_expected)

    def test04_rpt_contacts_qs(self):
        '''Testing Report: Not expected any result'''
        url = "/admin/its/report/2013"
        doc = self._get_elem_from_url(url)

        result = self._get_list_from_element(doc, "#rpt-contacts > tbody > tr > td", attr="object.text")
        result_expected = []
        self.assertEqual(result, result_expected)