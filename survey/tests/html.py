"""
run client tests
"""

from __future__ import absolute_import
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

import lxml.html


class SurveyHTMLTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.uinfo = {"username": "admin", "password": "admin02pass"}
        cls.user = User.objects.create_user(cls.uinfo["username"], "admin@example.com", cls.uinfo["password"])
        cls.user.is_staff = True
        cls.user.save()
        cls.client = Client()

    def setUp(self):
        self.is_logged_in = self.client.login(username=self.uinfo["username"], password=self.uinfo["password"])

    def test01_login(self):
        self.assertTrue(self.user.is_staff, "Expected user to be a staff")
        self.assertTrue(self.is_logged_in, "Expected .login to return true")


    def test02_emailInput(self):
        '''
        Test for email input field in the survey/add page
        http://projects.gnstudio.biz/T379
        '''

        url = "/admin/survey/survey/add/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))

        doc = lxml.html.fromstring(resp.content)

        selector = "input#slug"
        elem = doc.cssselect(selector)
        self.assertTrue(isinstance(elem, list), "Expect '%s' to return a list" % selector)

        # Test for:
        # <input id="slug" type="text" name="slug" class="validate[required]" data-prompt-position="topLeft" placeholder="Slug" value="">
        self.assertEqual(elem[0].get("data-prompt-position"), "topLeft", "Expected .data-prompt-position to be 'topLeft' but got '%s'" % elem[0].get("data-prompt-position"))
        self.assertEqual(elem[0].get("class"), "validate[required]", "Expected .data-prompt-position to be 'validate[required]' but got '%s'" % elem[0].get("class"))
