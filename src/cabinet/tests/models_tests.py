'''
Test for cabinet models
'''

import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

from cabinet.models import Cabinet, UploadedFile, UserFile, UserRefFile, UserCertFile
from campaigns.models import Event

class CabinetModelTestCase(TestCase):
    fixtures = ['initial_data', 'users_tests.json']
    def setUp(self):
        # Get the normal user
        self.user = User.objects.get(pk=3)
        # Get the staff user
        self.staff = User.objects.get(pk=2)

        self.event = Event.objects.create(
            date=datetime.date(2014,7,4),
            title="Teste Event for File"
        )
        self.cabinet_file = Cabinet.objects.get(pk=UserRefFile.CABINET_ID)
        self.cabinet_certificate = Cabinet.objects.get(pk=UserCertFile.CABINET_ID)
        self.refile = UploadedFile.objects.create(
            title="A Test File",
            file_ref=SimpleUploadedFile('reference.pdf', 'This is the reference file'),
            cabinet=self.cabinet_file,
            owner=self.staff
        )
        self.certfile = UploadedFile.objects.create(
            title="A Test Certificate",
            file_ref=SimpleUploadedFile('certificate.pdf', 'This is the certificate file'),
            cabinet=self.cabinet_certificate,
            owner=self.staff
        )

    def test01_UserRefFile(self):
        '''
        Should be able to create a normal file
        '''
        self.assertIsNotNone(self.refile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.refile.cabinet_id, self.cabinet_file.pk, "Expected cabinet to be %s but got %s" % (self.refile.cabinet, self.cabinet_file.pk))

        user_file = UserRefFile(
            user=self.user,
            file=self.refile,
            event=self.event
        )
        user_file.save()
        self.assertIsNotNone(user_file.date_created, "Expected UserRefFile.date_created to be populated.")
        self.assertEqual(user_file.file_id, self.refile.pk, "Expected user_file.file_id to be %s but got %s" % (user_file.file_id, self.refile.pk))
        self.assertEqual(user_file.event.title, self.event.title, "Expected user_file.event.title to be '%s' but got '%s" % (self.event.title, user_file.event.title))

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
        self.assertRaises(IntegrityError, user_file.save)


    def test10_UserCertFile(self):
        '''
        Adding a certificate
        '''
        self.assertIsNotNone(self.certfile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.certfile.cabinet_id, 2, "Expected cabinet to be %s but got %s" % (self.certfile.cabinet, self.cabinet_file.pk))

        user_cert = UserCertFile(
            user=self.user,
            file=self.certfile,
            expiry=datetime.date(2012,7,10)
        )
        user_cert.save()
        self.assertEqual(user_cert.user_id, self.user.pk, "Expected user_id to be %s but got %s" % (self.user.pk, user_cert.user_id))
        self.assertFalse(user_cert.is_valid, "Expected certificate not to be valid.")

    def test11_UserCertFile_error(self):
        '''
        Adding an invalid certificate
        '''
        self.assertIsNotNone(self.refile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.refile.cabinet_id, self.cabinet_file.pk, "Expected cabinet to be %s but got %s" % (self.refile.cabinet, self.cabinet_file.pk))

        user_cert = UserCertFile(
            user=self.user,
            file=self.refile,
            expiry=datetime.date(2012,7,10)
        )
        self.assertRaises(IntegrityError, user_cert.save)

    def test12_userCertFile_is_valid(self):
        '''
        Check certificate is valid logic
        '''
        today = datetime.date.today()

        # Set certificate to expire in 20 days, and should be valid
        expiry = today + datetime.timedelta(20)
        user_cert = UserCertFile(
            user=self.user,
            file=self.certfile,
            expiry=expiry
        )
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate with '%s' expiry to be valid." % expiry)

        # Set certificate to expire today, and should be valid
        user_cert.expiry = today
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate to be valid on the expiry day.")

        # Set the expiry to 10 days from ago, and should be invalid
        expiry = today - datetime.timedelta(10)
        user_cert.expiry = expiry
        user_cert.save()
        self.assertFalse(user_cert.is_valid, "Expected certificate with '%s' expiry NOT to be valid." % expiry)


    def test20_UploadedFile_delete(self):
        '''
        Cascade delete from UploadedFile should work
        '''

        self.assertEqual(UploadedFile.objects.count(), 2, "Expected UploadedFile to have 2 entries.")

        user_file = UserRefFile.objects.create(
            user=self.user,
            file=self.refile
        )
        staff_file = UserRefFile.objects.create(
            user=self.staff,
            file=self.refile
        )
        user_cert = UserCertFile.objects.create(
            user=self.user,
            file=self.certfile,
            expiry=datetime.date(2012,7,10)
        )

        self.assertEqual(UserFile.objects.count(), 3, "Expected UserRefFile to have 3 entries but got '%d'." % UserFile.objects.count())
        self.assertEqual(UserRefFile.objects.count(), 2, "Expected UserRefFile to have 2 entries but got '%d'." % UserRefFile.objects.count())
        self.assertEqual(UserCertFile.objects.count(), 1, "Expected UserCertFile to have 1 entry but got '%d'." % UserCertFile.objects.count())

        for file in UploadedFile.objects.all():
            file.delete()

        self.assertEqual(UserFile.objects.count(), 0, "Expected UserRefFile to have 0 entries but got '%d'." % UserFile.objects.count())
        self.assertEqual(UploadedFile.objects.count(), 0, "Expected UploadedFile to have 0 entries but got '%d'." % UploadedFile.objects.count())
        self.assertEqual(UserRefFile.objects.count(), 0, "Expected UserRefFile to have 0 entries but got '%d'." % UserRefFile.objects.count())
        self.assertEqual(UserCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry but got '%d'." % UserCertFile.objects.count())

    def test21_UserFile_delete(self):
        '''
        Cascade delete from UserRefFile and UserCertFile should work upto UserFile but not UploadedFile
        '''

        self.assertEqual(UploadedFile.objects.count(), 2, "Expected UploadedFile to have 2 entries.")

        user_file = UserRefFile.objects.create(
            user=self.user,
            file=self.refile
        )
        staff_file = UserRefFile.objects.create(
            user=self.staff,
            file=self.refile
        )
        user_cert = UserCertFile.objects.create(
            user=self.user,
            file=self.certfile,
            expiry=datetime.date(2012,7,10)
        )

        self.assertEqual(UserFile.objects.count(), 3, "Expected UserRefFile to have 3 entries but got '%d'." % UserFile.objects.count())
        self.assertEqual(UserRefFile.objects.count(), 2, "Expected UserRefFile to have 2 entries but got '%d'." % UserRefFile.objects.count())
        self.assertEqual(UserCertFile.objects.count(), 1, "Expected UserCertFile to have 1 entry but got '%d'." % UserCertFile.objects.count())

        # Testing cascade delete for certificate file
        user_cert.delete()
        self.assertEqual(UserFile.objects.count(), 2, "Expected UserRefFile to have 2 entries but got '%d'." % UserFile.objects.count())
        self.assertEqual(UploadedFile.objects.count(), 2, "Expected UploadedFile to have 2 entries but got '%d'." % UploadedFile.objects.count())
        self.assertEqual(UserRefFile.objects.count(), 2, "Expected UserRefFile to have 2 entries but got '%d'." % UserRefFile.objects.count())
        self.assertEqual(UserCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry but got '%d'." % UserCertFile.objects.count())

        # Testing cascade delete for reference file
        user_file.delete()
        self.assertEqual(UserFile.objects.count(), 1, "Expected UserRefFile to have 1 entries but got '%d'." % UserFile.objects.count())
        self.assertEqual(UploadedFile.objects.count(), 2, "Expected UploadedFile to have 2 entries but got '%d'." % UploadedFile.objects.count())
        self.assertEqual(UserRefFile.objects.count(), 1, "Expected UserRefFile to have 1 entries but got '%d'." % UserRefFile.objects.count())
        self.assertEqual(UserCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry but got '%d'." % UserCertFile.objects.count())



