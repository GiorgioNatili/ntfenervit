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
from django.core.exceptions import ObjectDoesNotExist

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from cabinet.models import UserRefFile, UserCertFile

# ToDo: add a another test to make sure user does not have access to the admin urls

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
TEST_MEDIA_ROOT=os.path.join(tempfile.mkdtemp(prefix="ntfenervit_utest_"), "media")


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

    def _upload_url(self, type):
        return "/admin/cabinet/%d/%s/add" % (self.user.id, type)

    def _edit_url(self, type, user_file_id):
        return "/admin/cabinet/%d/%s/%d" % (self.user.id, type, user_file_id)

    def _upload_file(self, type, **kwargs):
        """
        Private method to perform and check file upload.
        :param type: `ref` or `cert`
        :param kwargs: Initial dictionary that serve as data to post
        :return: Dictionary that was used in the post request
        """

        # Read the params that is meant for this method only
        if "user_file_id" in kwargs:
            user_file_id = kwargs["user_file_id"]
            del kwargs["user_file_id"]
        else:
            user_file_id = None

        if "file_path" in kwargs:
            file_path = kwargs["file_path"]
            del kwargs["file_path"]
        else:
            file_path = None

        if "expect_error" in kwargs:
            expect_error = True
            del kwargs["expect_error"]
        else:
            expect_error = False

        # Customize the user_file object based on type
        if type == "ref":
            user_file_class = UserRefFile
        else:
            user_file_class = UserCertFile
        kwargs["cabinet"] = user_file_class.CABINET_ID

        # Get the url based on action
        if kwargs["action"] == "add":
            url = self._upload_url(type)
        else:
            url = self._edit_url(type, user_file_id)

        # Add the other needed info
        kwargs.update({
            "user_id": self.user.id,
            "owner": self.admin.id,
            "referer": "/admin/"
        })

        # Only send file for upload if not delete action and that file_path is provided
        if kwargs["action"] == "delete" or file_path is None:
            resp = self.client.post(url, kwargs)
        else: # assume action == add or edit
            source_file = os.path.join(SCRIPT_DIR, file_path)
            with open(source_file, "r") as fh:
                kwargs["file_ref"] = fh
                resp = self.client.post(url, kwargs)

        if expect_error:
            self.assertEqual(resp.status_code, 200, "Expected '%s' to return 200 but got %s" % (url, resp.status_code))
        else:
            self.assertEqual(resp.status_code, 302, "Expected '%s' to return 302 but got %s" % (url, resp.status_code))
            self.assertRegexpMatches(resp.get("location"), r'\/admin\/$', "Expect to redirect to url ending '/admin/' but got '%s'" % resp.get("location"))

        # Make sure delete works
        if kwargs["action"] == "delete":
            self.assertRaises(ObjectDoesNotExist, UserRefFile.objects.get, pk=user_file_id)
            user_file = None
        elif expect_error:
            user_file = None
        else:
            # Make sure that database entry is created
            user_file = user_file_class.objects.get(file__title=kwargs["title"])
            self.assertEqual(user_file.user_id, kwargs["user_id"])

        return (user_file, kwargs, resp)


class CabinetAdminHTMLTestCase(BaseHTMLTestCase):
    '''
    Test Admin GUI
    '''
    fixtures = ['initial_data', 'users_tests', 'contacts_tests']

    def setUp(self):
        self.admin = User.objects.get(pk=1)
        self.user = User.objects.get(pk=3)
        self.is_logged_in = self.client.login(username=self.admin.username, password="devel02")


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
    User File Testing Common Methods
    '''


    '''
    File Testing
    '''
    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test10_addUserRefFile(self):
        """
        Make sure that file upload works
        """

        # Make sure needed fields exists on the add page
        url_upload = self._upload_url("ref")
        doc = self._get_elem_from_url(url_upload)
        for field_selector in ('#id_file_ref', '#id_event_title', '#id_title'):
            elem = doc.cssselect(field_selector)
            self.assertTrue(elem, "Selector '%s' should not to be empty" % field_selector)

        # Upload an file
        user_file, test_data, resp = self._upload_file("ref", action="add", title="Presentation File BQWy4ukoFq", file_path="res/presentation.pdf")
        user_file_id = user_file.id

        # Make sure that file has been uploaded
        uploaded_file = user_file.file.file_fullpath()
        self.assertTrue(os.path.isfile(uploaded_file), "Expected local file to exists at: %s" % uploaded_file)
        self.assertTrue(uploaded_file.startswith(TEST_MEDIA_ROOT), "Expected file to start with '%s'.  Local file: %s" % (TEST_MEDIA_ROOT, uploaded_file))

        # Make sure that file can be viewed and that title matches
        url = self._edit_url("ref", user_file_id)
        doc = self._get_elem_from_url(url)

        title = self._get_list_from_element(doc,selector="#id_title", attr="value")
        self.assertTrue(title, "Expect title to exists.")
        self.assertEqual(title[0], test_data["title"])

        # Make sure that path shown on the page point to the same file
        file_path = self._get_list_from_element(doc,"form#file_form > div > div > ul > li > a",attr="href")
        self.assertTrue(file_path, "Expect path to the file to exists in the form.")
        self.assertRegexpMatches(file_path[0], "presentation.pdf$", "Expect file path to end with 'presentation.pdf' but got '%s'" % file_path)

    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test11_editUserRefFile(self):
        """
        Make sure that file edit works
        """

        # Upload an file
        user_file, test_data, resp = self._upload_file("ref", action="add", title="Editing a file s81a4oju1p", file_path="res/presentation.pptx")
        user_file_id = user_file.id
        uploaded_file = user_file.file.file_fullpath()
        url_edit = self._edit_url("ref", user_file_id)

        # Make sure that edit only title works
        user_file, test_data_edited, resp = self._upload_file("ref", action="edit", user_file_id=user_file_id, title="A file edited HCffL9jl9U")
        self.assertEqual(user_file.id, user_file_id)
        self.assertTrue(os.path.isfile(uploaded_file), "Expected local file exists: %s" % uploaded_file)

        # Check GUI
        doc = self._get_elem_from_url(url_edit)
        title = self._get_list_from_element(doc,selector="#id_title", attr="value")
        self.assertTrue(title, "Expect title to exists.")
        self.assertEqual(title[0], test_data_edited["title"])

        # Make sure that edit title and file works
        user_file, test_data_edited2, resp = self._upload_file("ref", action="edit", user_file_id=user_file_id, title="File changed dhVRNCsJJL", file_path="res/presentation.pdf")
        uploaded_file = user_file.file.file_fullpath()
        self.assertEqual(user_file.id, user_file_id)

        # Check GUI
        doc = self._get_elem_from_url(url_edit)
        title = self._get_list_from_element(doc,selector="#id_title", attr="value")
        self.assertTrue(title, "Expect title to exists.")
        self.assertEqual(title[0], test_data_edited2["title"])

        # Make sure that delete works
        user_file, test_data_deleted, resp = self._upload_file("ref", action="delete", user_file_id=user_file_id)
        self.assertFalse(os.path.isfile(uploaded_file), "Expected local file to have been deleted: %s" % uploaded_file)

    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test12_wrongUserRefFile(self):
        '''
        Make sure that invalid file upload is rejected
        '''
        user_file, test_data, resp = self._upload_file("ref", action="add", title="Adding a new presentation zvFAzzdkYC", file_path="res/presentation.txt", expect_error=True)
        self.assertIsNone(user_file)
        doc = lxml.html.fromstring(resp.content)

        elems = self._get_elements(doc, selector="form#file_form > .alert-error > ul > li")
        self.assertIsInstance(elems, list)
        self.assertEqual(elems[0].text, "File con estensione '.txt' non supportato.")

    '''
    Certificate Testing
    '''
    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test20_addUserCertFile(self):
        """
        Make sure that file upload works
        """

        # Make sure needed fields exists on the add page
        url_upload = self._upload_url("cert")
        doc = self._get_elem_from_url(url_upload)
        for field_selector in ('#id_file_ref', '#id_expiry', '#id_title'):
            elem = doc.cssselect(field_selector)
            self.assertTrue(elem, "Selector '%s' should not to be empty" % field_selector)

        # Upload an file
        # datetime.datetime.strptime(test_data["expiry"], "%d/%m/%Y").date()
        expiry = datetime.date.today() + datetime.timedelta(20)
        user_file, test_data, resp = self._upload_file("cert", action="add", title="Certification File qwa1g31SgT", expiry=expiry.strftime("%d/%m/%Y"), file_path="res/certificate.png")
        user_file_id = user_file.id
        self.assertEqual(user_file.expiry, expiry)

        # Make sure that file has been uploaded
        uploaded_file = user_file.file.file_fullpath()
        self.assertTrue(os.path.isfile(uploaded_file), "Expected local file to exists at: %s" % uploaded_file)
        self.assertTrue(uploaded_file.startswith(TEST_MEDIA_ROOT), "Expected file to start with '%s'.  Local file: %s" % (TEST_MEDIA_ROOT, uploaded_file))

        # Make sure that file can be viewed and that title matches
        url = self._edit_url("cert", user_file_id)
        doc = self._get_elem_from_url(url)

        title = self._get_list_from_element(doc,selector="#id_title", attr="value")
        self.assertTrue(title, "Expect title to exists.")
        self.assertEqual(title[0], test_data["title"])

        # Make sure that path shown on the page point to the same file
        file_path = self._get_list_from_element(doc,"form#file_form > div > div > ul > li > a",attr="href")
        self.assertTrue(file_path, "Expect path to the file to exists in the form.")
        self.assertRegexpMatches(file_path[0], "certificate.png$", "Expect file path to end with 'certificate.png' but got '%s'" % file_path)

    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test21_editUserCertFile(self):
        """
        Make sure that file edit works
        """

        # Upload an file
        user_file, test_data, resp = self._upload_file("cert", action="add", title="Editing a certificate XrLDoOQl8H", expiry="07/12/2035", file_path="res/certificate.pdf")
        user_file_id = user_file.id
        uploaded_file = user_file.file.file_fullpath()
        url_edit = self._edit_url("cert", user_file_id)

        # Make sure that edit only title works
        user_file, test_data_edited, resp = self._upload_file("cert", action="edit", user_file_id=user_file_id, expiry="02/05/2040", title="Certificate edited DNjWOYzjTy")
        self.assertEqual(user_file.id, user_file_id)
        self.assertTrue(os.path.isfile(uploaded_file), "Expected local file exists: %s" % uploaded_file)
        self.assertEqual(user_file.expiry, datetime.datetime.strptime(test_data_edited["expiry"], "%d/%m/%Y").date())

        # Check GUI
        doc = self._get_elem_from_url(url_edit)

        title = self._get_list_from_element(doc,selector="#id_title", attr="value")
        self.assertTrue(title, "Expect title to exists.")
        self.assertEqual(title[0], test_data_edited["title"])

        expiry = self._get_list_from_element(doc,selector="#id_expiry", attr="value")
        self.assertTrue(expiry, "Expect expiry to exists.")
        self.assertEqual(expiry[0], test_data_edited["expiry"])


        # Make sure that edit title and file works
        user_file, test_data_edited2, resp = self._upload_file("cert", action="edit", user_file_id=user_file_id, expiry="30/06/2033", title="Certificate changed XDEZvMXhDE", file_path="res/certificate.png")
        uploaded_file = user_file.file.file_fullpath()
        self.assertEqual(user_file.id, user_file_id)

        # Check GUI
        doc = self._get_elem_from_url(url_edit)

        title = self._get_list_from_element(doc,selector="#id_title", attr="value")
        self.assertTrue(title, "Expect title to exists.")
        self.assertEqual(title[0], test_data_edited2["title"])

        expiry = self._get_list_from_element(doc,selector="#id_expiry", attr="value")
        self.assertTrue(expiry, "Expect expiry to exists.")
        self.assertEqual(expiry[0], test_data_edited2["expiry"])


        # Make sure that delete works
        user_file, test_data_deleted, resp = self._upload_file("cert", action="delete", user_file_id=user_file_id)
        self.assertFalse(os.path.isfile(uploaded_file), "Expected local file to have been deleted: %s" % uploaded_file)

    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test22_wrongUserCertFile(self):
        '''
        Make sure that invalid certificate upload is rejected
        '''
        # Upload an file
        user_file, test_data, resp = self._upload_file("cert", action="add", title="Adding a new certificate Zh5VbQurCe", expiry="07/12/2040", file_path="res/certificate.ppt", expect_error=True)
        self.assertIsNone(user_file)
        doc = lxml.html.fromstring(resp.content)

        elems = self._get_elements(doc, selector="form#file_form > .alert-error > ul > li")
        self.assertIsInstance(elems, list)
        self.assertEqual(elems[0].text, "File con estensione '.ppt' non supportato.")






class CabinetHTMLTestCase(BaseHTMLTestCase):
    '''
    Test Admin GUI
    '''
    fixtures = ['initial_data', 'users_tests', 'contacts_tests']

    def setUp(self):
        self.admin = User.objects.get(pk=1)
        self.user = self.admin
        self.is_logged_in = self.client.login(username=self.user.username, password="devel02")

    def test01_login(self):
        """
        Make sure admin user is logged in
        """
        # self.assertFalse(self.user.is_staff, "Expected user NOT to be a staff")
        self.assertTrue(self.is_logged_in, "Expected .login to return true")

    def test02_userFile(self):
        '''
        Make sure user files are shown correctly in the GUI
        '''

        # Upload normal files
        ref_titles = ["Presentation File RhBxLTn4Qe", "Another Presentation X1XVZPSTk2"]
        ref_files = []

        res_ref = self._upload_file("ref", action="add", title=ref_titles[0], file_path="res/presentation.pdf")
        res_url = res_ref[0].file.file_ref.url
        self.assertRegexpMatches(res_url, "presentation.*pdf$")
        ref_files.append(res_url)

        res_ref = self._upload_file("ref", action="add", title=ref_titles[1], file_path="res/presentation.pptx")
        res_url = res_ref[0].file.file_ref.url
        self.assertRegexpMatches(res_url, "presentation.*pptx$")
        ref_files.append(res_url)

        # Upload certificates
        cert_titles = ["Certificate juz84oz57i", "Another Certificate Og191Ecrg7"]
        cert_files = []

        res_cert = self._upload_file("cert", action="add", title=cert_titles[0], expiry="07/12/2035", file_path="res/certificate.pdf")
        res_url = res_cert[0].file.file_ref.url
        self.assertRegexpMatches(res_url, "certificate.*pdf$")
        cert_files.append(res_url)

        res_cert = self._upload_file("cert", action="add", title=cert_titles[1], expiry="07/12/2035", file_path="res/certificate.png")
        res_url = res_cert[0].file.file_ref.url
        self.assertRegexpMatches(res_url, "certificate.*png$")
        cert_files.append(res_url)

        # Go to the frontend
        url = "/frontend/main/"
        doc = self._get_elem_from_url(url)

        # Check normal files
        elems = self._get_list_from_element(doc, selector="#ref_table > tbody > tr > td > a", attr="object.text")
        self.assertEqual(elems, ref_titles)

        elems = self._get_list_from_element(doc, selector="#ref_table > tbody > tr > td > a", attr="href")
        self.assertEqual(elems, ref_files)

        # Check certificates
        elems = self._get_list_from_element(doc, selector="#cert_table > tbody > tr > td > a", attr="object.text")
        self.assertEqual(elems, cert_titles)

        elems = self._get_list_from_element(doc, selector="#cert_table > tbody > tr > td > a", attr="href")
        self.assertEqual(elems, cert_files)

    def test03_expiredCertificate(self):
        '''
        Make sure that expired certificate is displayed correctly
        '''

        # Set the expiry to 10 days ago
        expiry = datetime.date.today() - datetime.timedelta(10)
        cert_tile = "Certificate of GDND8wSVDz"
        res_cert = self._upload_file("cert", action="add", title=cert_tile, expiry=expiry.strftime("%d/%m/%Y"), file_path="res/certificate.pdf")

        # Go to the frontend
        url = "/frontend/main/"
        doc = self._get_elem_from_url(url)

        # Get the entry
        elems = self._get_list_from_element(doc, selector="#cert_table > tbody > tr > td > span.label-danger", attr="object.text")
        self.assertEqual(elems, ["scaduto"])
