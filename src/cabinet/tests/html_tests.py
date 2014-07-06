"""
run client tests
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import lxml.html

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
        self.assertTrue(self.admin.is_staff, "Expected admin to be a staff")
        self.assertTrue(self.is_logged_in, "Expected .login to return true")

    def test02_add(self):
        url = "/admin/backend/utenti/details/%d/" % self.user.id
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))
        doc = lxml.html.fromstring(resp.content)

        selector = "form#company_form > div > div > ul > li > input[name='email']"
        elem = doc.cssselect(selector)
        self.assertTrue(isinstance(elem, list), "Expect '%s' to return a list" % selector)


        self.assertEqual(elem[0].get("value"),"user.one@example.com", "Expect email field to be 'user.one@example.com' but got '%s'" % elem[0].get("value"))


