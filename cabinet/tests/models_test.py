'''
Test for cabinet models
'''

from django.test import TestCase
from django.contrib.auth.models import User
from cabinet.models import Cabinet, UploadedFile, UserRefFile, UserCertFile

from django.db import IntegrityError
from django.core.exceptions import ValidationError


class CabinetTestCase(TestCase):
    fixtures = ['initial_data']
    def setUp(self):
        self.user = User.objects.create_user("testuser", "testuser@example.com", "user02pass")
        self.cabinet_file = Cabinet.objects.get(pk=1)
        self.cabinet_certificate = Cabinet.objects.get(pk=2)
        self.refile = UploadedFile.objects.create(
            desc="A Test File",
            cabinet=self.cabinet_file,
            owner=self.user
        )
        self.certfile = UploadedFile.objects.create(
            desc="A Test Certificate",
            cabinet=self.cabinet_certificate,
            owner=self.user
        )

    def test01_UserRefFile(self):
        '''
        Should be able to create a normal file
        '''
        self.assertIsNotNone(self.refile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.refile.cabinet_id, self.cabinet_file.pk, "Expected cabinet to be %s but got %s" % (self.refile.cabinet, self.cabinet_file.pk))

        user_file = UserRefFile(
            user=self.user,
            file=self.refile
        )
        user_file.save()
        self.assertIsNotNone(user_file.date_created, "Expected UserRefFile.date_created to be populated.")
        self.assertEqual(user_file.file_id, self.refile.pk, "Expected user_file.file_id to be %s but got %s" % (user_file.file_id, self.refile.pk))

        # Second user/file combination should raise integrity error
        user_file2 = UserRefFile(
            user=self.user,
            file=self.refile
        )
        self.assertRaises(IntegrityError, user_file2.save)

    def test02_UserRefFile_error(self):
        '''
        Adding a file from the certificate to UserFile should raise error
        '''
        self.assertIsNotNone(self.certfile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.certfile.cabinet_id, 2, "Expected cabinet to be %s but got %s" % (self.certfile.cabinet, self.cabinet_file.pk))

        # .clean should raise a ValidationError but .save should raise IntegrityError
        user_file = UserRefFile(
            user=self.user,
            file=self.certfile
        )
        self.assertRaises(ValidationError, user_file.clean)
        self.assertRaises(IntegrityError, user_file.save)


    def test03_UserCertFile(self):
        '''
        Adding a certificate
        '''
        self.assertIsNotNone(self.certfile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.certfile.cabinet_id, 2, "Expected cabinet to be %s but got %s" % (self.certfile.cabinet, self.cabinet_file.pk))

        user_cert = UserCertFile(
            user=self.user,
            file=self.certfile,
            expiry="2013-07-10"
        )
        user_cert.save()
        self.assertEqual(user_cert.user_id, self.user.pk, "Expected user_id to be %s but got %s" % (self.user.pk, user_cert.user_id))

    def test04_UserCertFile_error(self):
        '''
        Adding a certificate
        '''
        self.assertIsNotNone(self.refile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.refile.cabinet_id, self.cabinet_file.pk, "Expected cabinet to be %s but got %s" % (self.refile.cabinet, self.cabinet_file.pk))

        user_cert = UserCertFile(
            user=self.user,
            file=self.refile,
            expiry="2013-07-10"
        )
        self.assertRaises(ValidationError, user_cert.clean)
        self.assertRaises(IntegrityError, user_cert.save)

    def test05_UploadedFile_delete(self):
        '''
        Cascade delete from UploadedFile should work
        '''

        self.assertEqual(UploadedFile.objects.count(), 2, "Expected UploadedFile to have 2 entries.")

        user_file = UserRefFile.objects.create(
            user=self.user,
            file=self.refile
        )
        user_cert = UserCertFile.objects.create(
            user=self.user,
            file=self.certfile,
            expiry="2013-07-10"
        )
        self.assertEqual(UserRefFile.objects.count(), 2, "Expected UserRefFile to have 2 entries.")
        self.assertEqual(UserCertFile.objects.count(), 1, "Expected UserCertFile to have 1 entry.")

        # Testing cascade delete for certificate file
        self.certfile.delete()
        self.assertEqual(UploadedFile.objects.count(), 1, "Expected UploadedFile to have 1 entries.")
        self.assertEqual(UserRefFile.objects.count(), 1, "Expected UserRefFile to have 1 entries.")
        self.assertEqual(UserCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry.")

        # Testing cascade delete for reference file
        self.refile.delete()
        self.assertEqual(UploadedFile.objects.count(), 0, "Expected UploadedFile to have 0 entries.")
        self.assertEqual(UserRefFile.objects.count(), 0, "Expected UserRefFile to have 0 entries.")
        self.assertEqual(UserCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry.")