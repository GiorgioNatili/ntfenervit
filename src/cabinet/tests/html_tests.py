"""
run client tests
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import lxml.html

# ToDo: add a another test to make sure user does not have access to the admin urls

class CabinetHTMLTestCase(TestCase):
    fixtures = ['initial_data', 'users_tests', 'contacts_tests']

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    def setUp(self):
        self.admin = User.objects.get(pk=1)
        self.user = User.objects.get(pk=3)
        self.is_logged_in = self.client.login(username=self.admin.username, password="devel02")

    def test01_login(self):
        '''
        Make sure admin user is logged in
        '''
        self.assertTrue(self.admin.is_staff, "Expected admin to be a staff")
        self.assertTrue(self.is_logged_in, "Expected .login to return true")

    def test02_userDetailPage(self):
        url = "/admin/backend/utenti/details/%d/" % self.user.id
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))
        doc = lxml.html.fromstring(resp.content)

        # Make sure that email is from expected user
        selector = "form#company_form > div > div > ul > li > input[name='email']"
        elem = doc.cssselect(selector)
        self.assertTrue(elem, "Expect '%s' not to be empty" % selector)
        self.assertEqual(elem[0].get("value"), "user.one@example.com", "Expect email field to be 'user.one@example.com' but got '%s'" % elem[0].get("value"))

        # Make sure that files section exists
        selector = "#refFileTable"
        elem = doc.cssselect(selector)
        self.assertTrue(elem, "Expect '%s' not to be empty" % selector)

        # Make sure that certification section exists
        selector = "#certFileTable"
        elem = doc.cssselect(selector)
        self.assertTrue(elem, "Expect '%s' not to be empty" % selector)

    def test05_addFilePage(self):
        url = "/admin/cabinet/%d/ref/add" % self.user.id
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))
        doc = lxml.html.fromstring(resp.content)

        # Make sure needed fields exists
        for field_selector in ('#id_file_ref', '#id_event_title', '#id_title'):
            elem = doc.cssselect(field_selector)
            self.assertTrue(elem, "Expect '%s' not to be empty" % field_selector)

        def test05_addFilePage(self):
            url = "/admin/cabinet/%d/ref/add" % self.user.id
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))
        doc = lxml.html.fromstring(resp.content)

        # Make sure needed fields exists
        for field_selector in ('#id_file_ref', '#id_event_title', '#id_title'):
            elem = doc.cssselect(field_selector)
            self.assertTrue(elem, "Expect '%s' not to be empty" % field_selector)

    def test010_addCertificatePage(self):
        url = "/admin/cabinet/%d/cert/add" % self.user.id
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))
        doc = lxml.html.fromstring(resp.content)

        # Make sure needed fields exists
        for field_selector in ('#id_file_ref', '#id_expiry', '#id_title'):
            elem = doc.cssselect(field_selector)
            self.assertTrue(elem, "Expect '%s' not to be empty" % field_selector)
