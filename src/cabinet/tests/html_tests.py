"""
run client tests
"""

import os
import lxml.html
import tempfile
import re
import datetime

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from cabinet.models import UserRefFile, UserCertFile

# ToDo: add a another test to make sure user does not have access to the admin urls

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
TEST_MEDIA_ROOT=os.path.join(tempfile.mkdtemp(prefix="ntfenervit_utest_"), "media")

class CabinetHTMLTestCase(TestCase):
    fixtures = ['initial_data', 'users_tests', 'contacts_tests']

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    def setUp(self):
        self.admin = User.objects.get(pk=1)
        self.user = User.objects.get(pk=3)
        self.is_logged_in = self.client.login(username=self.admin.username, password="devel02")

    def _get_elem_from_url(self, url):
        """
        Private method to return a parsed element from url
        :param url: URL to retrieve HTML from
        :return: a parsed element
        """
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))
        doc = lxml.html.fromstring(resp.content)
        self.assertTrue(doc, "Failed to parse '%s'.  HTML:\n%s" % (url, resp.content))
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
        :param attr: Optional return given attribute instead of html
        :return: list of string
        """
        if selector:
            elem = self._get_elements(element, selector)
        else:
            elem = element

        if attr:
            result = [x.get(attr) for x in elem]
        else:
            result = [lxml.html.tostring(x) for x in elem]

        return result




    '''
    User Detail Page Testing
    '''
    def test01_login(self):
        """
        Make sure admin user is logged in
        """
        self.assertTrue(self.admin.is_staff, "Expected admin to be a staff")
        self.assertTrue(self.is_logged_in, "Expected .login to return true")

    def test02_userDetailPage(self):
        """
        Make sure that user detail page exists and getting the right user
        """
        doc = self._get_elem_from_url("/admin/backend/utenti/details/%d/" % self.user.id)

        # Make sure the user is as expected by checking email
        selector = "form#company_form > div > div > ul > li > input[name='email']"
        email = self._get_list_from_element(doc, selector, "value")
        self.assertGreater(len(email), 0, "Selector '%s' should not to be empty" % selector)
        self.assertEqual(email[0], "user.one@example.com", "Expect email field to be 'user.one@example.com' but got '%s'" % email[0])


    def test03_filesTable(self):
        """
        Make sure that Files Table is as expected
        """

        doc = self._get_elem_from_url("/admin/backend/utenti/details/%d/" % self.user.id)

        # Make sure that files section exists
        selector = "#refFileTable"
        tbl = doc.cssselect(selector)
        self.assertTrue(tbl, "Selector '%s' should not to be empty" % selector)

        # Check the header
        selector = "table > thead > tr > th > div"
        tbl_headers = self._get_list_from_element(tbl, selector=selector)
        expected_result = ['<div>Id</div>', '<div>Titolo</div>', '<div>Evento</div>', '<div>File</div>', '<div>Data</div>']
        self.assertEqual(tbl_headers, expected_result, "Expected '%s' but got '%s'" % (expected_result, tbl_headers))

        # No entry should exists in the table
        selector = "table > tbody > tr"
        tbl_rows = self._get_elements(tbl, selector=selector)
        self.assertFalse(tbl_rows, "No result expected from the Files table but got '%d' rows." % len(tbl_rows))


    def test04_certTable(self):
        """
        Make sure that Certificate Table is as expected
        Could be merged with test03_filesTable is performance becomes an issue
        """
        doc = self._get_elem_from_url("/admin/backend/utenti/details/%d/" % self.user.id)

        # Make sure that files section exists
        selector = "#certFileTable"
        tbl = doc.cssselect(selector)
        self.assertTrue(tbl, "Selector '%s' should not to be empty" % selector)

        # Check the header
        selector = "table > thead > tr > th > div"
        tbl_headers = self._get_list_from_element(tbl, selector=selector)
        expected_result = ['<div>Id</div>', '<div>Titolo</div>', '<div>Scadenza</div>', '<div>File</div>', '<div>Data</div>']
        self.assertEqual(tbl_headers, expected_result, "Expected '%s' but got '%s'" % (expected_result, tbl_headers))

        # No entry should exists in the table
        selector = "table > tbody > tr"
        tbl_rows = self._get_elements(tbl, selector=selector)
        self.assertFalse(tbl_rows, "No result expected from the Files table but got '%d' rows." % len(tbl_rows))




    '''
    Files testing
    '''
    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test10_addFilePage(self):
        """
        Make sure to add page exists
        """
        url = "/admin/cabinet/%d/ref/add" % self.user.id
        doc = self._get_elem_from_url(url)

        # Make sure needed fields exists
        for field_selector in ('#id_file_ref', '#id_event_title', '#id_title'):
            elem = doc.cssselect(field_selector)
            self.assertTrue(elem, "Selector '%s' should not to be empty" % field_selector)

        # Post a file
        test_file = os.path.join(SCRIPT_DIR, "res/presentation.pdf")
        test_data = {
            "title": "Presentation File BQWy4ukoFq",
            "event_title": "",
            "action": "add",
            "cabinet": UserRefFile.CABINET_ID,
            "user_id": self.user.id,
            "owner": self.admin.id,
            "referer": "/admin/"
        }
        with open(test_file, "r") as fh:
            test_data["file_ref"] = fh
            test_data["file_ref"] = fh
            resp = self.client.post(url, test_data)
            self.assertEqual(resp.status_code, 302, "Expected '%s' to return 302 but got %s" % (url, resp.status_code))
            self.assertRegexpMatches(resp.get("location"), r'\/admin\/$', "Expect to redirect to url ending '/admin/' but got '%s'" % resp.get("location"))

        # Make sure that db is updated correctly
        user_file = UserRefFile.objects.get(file__title=test_data["title"])
        self.assertEqual(user_file.user_id, test_data["user_id"])

        # Make sure that file has been uploaded
        uploaded_file = user_file.file.file_fullpath()

        self.assertTrue(os.path.isfile(uploaded_file), "Expected local file to exists at: %s" % uploaded_file)
        self.assertTrue(uploaded_file.startswith(TEST_MEDIA_ROOT), "Expected file to start with '%s'.  Local file: %s" % (TEST_MEDIA_ROOT, uploaded_file))


    '''
    User Detail Page Testing
    '''
    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test20_addCertificatePage(self):
        url = "/admin/cabinet/%d/cert/add" % self.user.id
        doc = self._get_elem_from_url(url)

        # Make sure needed fields exists
        for field_selector in ('#id_file_ref', '#id_expiry', '#id_title'):
            elem = doc.cssselect(field_selector)
            self.assertTrue(elem, "Selector '%s' should not to be empty" % field_selector)

        # Post a file
        test_file = os.path.join(SCRIPT_DIR, "res/presentation.pptx")
        test_data = {
            "title": "Powerpoint File Q0KrTVGuD9",
            "expiry": "07/12/2018",
            "action": "add",
            "cabinet": UserCertFile.CABINET_ID,
            "user_id": self.user.id,
            "owner": self.admin.id,
            "referer": "/admin/"
        }
        with open(test_file, "r") as fh:
            test_data["file_ref"] = fh
            test_data["file_ref"] = fh
            resp = self.client.post(url, test_data)
            self.assertEqual(resp.status_code, 302, "Expected '%s' to return 302 but got %s" % (url, resp.status_code))
            self.assertRegexpMatches(resp.get("location"), r'\/admin\/$', "Expect to redirect to url ending '/admin/' but got '%s'" % resp.get("location"))

        # Make sure that db is updated correctly
        user_file = UserCertFile.objects.get(file__title=test_data["title"])
        self.assertEqual(user_file.user_id, test_data["user_id"])
        self.assertEqual(user_file.expiry, datetime.datetime.strptime(test_data["expiry"], "%d/%m/%Y").date())

        # Make sure that file has been uploaded
        uploaded_file = user_file.file.file_fullpath()

        self.assertTrue(os.path.isfile(uploaded_file), "Expected local file to exists at: %s" % uploaded_file)
        self.assertTrue(uploaded_file.startswith(TEST_MEDIA_ROOT), "Expected file to start with '%s'.  Local file: %s" % (TEST_MEDIA_ROOT, uploaded_file))
