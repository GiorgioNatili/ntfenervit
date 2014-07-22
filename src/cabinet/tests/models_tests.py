'''
Test for cabinet models
'''

import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

from cabinet.models import Cabinet, UploadedFile, ContactFile, EventFile, ContactRefFile, ContactCertFile
from campaigns.models import Event
from contacts.models import Contact

class CabinetModelTestCase(TestCase):
    fixtures = ['initial_data', 'users_tests.json', 'contacts_tests.json', 'events_tests.json']
    def setUp(self):
        # Get the normal user
        self.contact = Contact.objects.get(owner=3)

        # Get the staff user
        self.staff_contact = Contact.objects.get(owner=2)
        self.staff = User.objects.get(pk=2)

        self.event = Event.objects.get(pk=1)

        self.cabinet_file = Cabinet.objects.get(pk=ContactRefFile.CABINET_ID)
        self.cabinet_certificate = Cabinet.objects.get(pk=ContactCertFile.CABINET_ID)
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
        self.eventfile = UploadedFile.objects.create(
            title="A Test Eventfile",
            file_ref=SimpleUploadedFile('eventdetail.pdf', 'This is the event detail file'),
            cabinet=self.cabinet_file,
            owner=self.staff
        )

    def test01_UserRefFile(self):
        '''
        Should be able to create a normal file
        '''
        self.assertIsNotNone(self.refile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.refile.cabinet_id, self.cabinet_file.pk, "Expected cabinet to be %s but got %s" % (self.refile.cabinet, self.cabinet_file.pk))

        user_file = ContactRefFile(
            contact=self.contact,
            file=self.refile,
            event=self.event
        )
        user_file.save()
        self.assertIsNotNone(user_file.date_created, "Expected UserRefFile.date_created to be populated.")
        self.assertEqual(user_file.file_id, self.refile.pk, "Expected user_file.file_id to be %s but got %s" % (user_file.file_id, self.refile.pk))
        self.assertEqual(user_file.event.title, self.event.title, "Expected user_file.event.title to be '%s' but got '%s" % (self.event.title, user_file.event.title))

        # Second user/file combination should raise integrity error
        user_file2 = ContactRefFile(
            contact=self.contact,
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
        user_file = ContactRefFile(
            contact=self.contact,
            file=self.certfile
        )
        self.assertRaises(IntegrityError, user_file.save)




    def test10_UserCertFile(self):
        '''
        Adding a certificate
        '''
        self.assertIsNotNone(self.certfile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.certfile.cabinet_id, 2, "Expected cabinet to be %s but got %s" % (self.certfile.cabinet, self.cabinet_file.pk))

        user_cert = ContactCertFile(
            contact=self.contact,
            file=self.certfile,
            expiry=datetime.date(2012,7,10)
        )
        user_cert.save()
        self.assertEqual(user_cert.contact_id, self.contact.pk, "Expected user_id to be %s but got %s" % (self.contact.pk, user_cert.contact_id))
        self.assertFalse(user_cert.is_valid, "Expected certificate not to be valid.")

    def test11_UserCertFile_error(self):
        '''
        Adding an invalid certificate
        '''
        self.assertIsNotNone(self.refile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.refile.cabinet_id, self.cabinet_file.pk, "Expected cabinet to be %s but got %s" % (self.refile.cabinet, self.cabinet_file.pk))

        user_cert = ContactCertFile(
            contact=self.contact,
            file=self.refile,
            expiry=datetime.date(2012,7,10)
        )
        self.assertRaises(IntegrityError, user_cert.save)

    def test12_userCertFile_expiry(self):
        '''
        Check certificate is valid logic and duration
        '''
        today = datetime.date.today()

        # Set certificate to expire in 20 days, and should be valid
        expiry = today + datetime.timedelta(20)
        user_cert = ContactCertFile(
            contact=self.contact,
            file=self.certfile,
            expiry=expiry
        )
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate with '%s' expiry to be valid." % expiry)
        self.assertEqual(user_cert.duration, 0, "Expected expiry '%s' to result in duration of '0' but got '%s'" % (expiry,user_cert.duration))
        self.assertEqual(user_cert.duration_code, "1y-", "Expected expiry '%s' to result in duration of '1y-' but got '%s'" % (expiry,user_cert.duration_code))

        # Set certificate to expire today, and should be valid
        user_cert.expiry = today
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate to be valid on the expiry day.")
        self.assertEqual(user_cert.duration, 0, "Expected expiry '%s' to result in duration of '0' but got '%s'" % (expiry,user_cert.duration))
        self.assertEqual(user_cert.duration_code, "1y-", "Expected expiry '%s' to result in duration of '1y-' but got '%s'" % (expiry,user_cert.duration_code))

        # Set the expiry to 10 days ago, and should be invalid
        expiry = today - datetime.timedelta(10)
        user_cert.expiry = expiry
        user_cert.save()
        self.assertFalse(user_cert.is_valid, "Expected certificate with '%s' expiry NOT to be valid." % expiry)
        self.assertEqual(user_cert.duration, -1, "Expected expiry '%s' to result in duration of '-1' but got '%s'" % (expiry,user_cert.duration))
        self.assertEqual(user_cert.duration_code, "expired", "Expected expiry '%s' to result in duration of 'expired' but got '%s'" % (expiry,user_cert.duration_code))

        # Set the expiry to 1 year from now, and should be invalid
        expiry = today + datetime.timedelta(365 + 10)
        user_cert.expiry = expiry
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate with '%s' expiry be valid." % expiry)
        self.assertEqual(user_cert.duration, 1, "Expected expiry '%s' to result in duration of '1' but got '%s'" % (expiry,user_cert.duration))
        self.assertEqual(user_cert.duration_code, "1y-", "Expected expiry '%s' to result in duration of '1y-' but got '%s'" % (expiry,user_cert.duration_code))

        # Set the expiry to 2 years from ago, and should be invalid
        expiry = today + datetime.timedelta(365 * 2 + 10)
        user_cert.expiry = expiry
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate with '%s' expiry be valid." % expiry)
        self.assertEqual(user_cert.duration, 2, "Expected expiry '%s' to result in duration of '2' but got '%s'" % (expiry,user_cert.duration))
        self.assertEqual(user_cert.duration_code, "2y", "Expected expiry '%s' to result in duration of '2y' but got '%s'" % (expiry,user_cert.duration_code))

        # Set the expiry to 3 years from ago, and should be invalid
        expiry = today + datetime.timedelta(365 * 3 + 10)
        user_cert.expiry = expiry
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate with '%s' expiry be valid." % expiry)
        self.assertEqual(user_cert.duration, 3, "Expected expiry '%s' to result in duration of '3' but got '%s'" % (expiry,user_cert.duration))
        self.assertEqual(user_cert.duration_code, "3y", "Expected expiry '%s' to result in duration of '3y' but got '%s'" % (expiry,user_cert.duration_code))

        # Set the expiry to 4 years from ago, and should be invalid
        expiry = today + datetime.timedelta(365 * 4 + 10)
        user_cert.expiry = expiry
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate with '%s' expiry be valid." % expiry)
        self.assertEqual(user_cert.duration, 4, "Expected expiry '%s' to result in duration of '4' but got '%s'" % (expiry,user_cert.duration))
        self.assertEqual(user_cert.duration_code, "4y+", "Expected expiry '%s' to result in duration of '4y+' but got '%s'" % (expiry,user_cert.duration_code))

        # Set the expiry to 7 years from ago, and should be invalid
        expiry = today + datetime.timedelta(365 * 7 + 10)
        user_cert.expiry = expiry
        user_cert.save()
        self.assertTrue(user_cert.is_valid, "Expected certificate with '%s' expiry be valid." % expiry)
        self.assertEqual(user_cert.duration, 7, "Expected expiry '%s' to result in duration of '7' but got '%s'" % (expiry,user_cert.duration))
        self.assertEqual(user_cert.duration_code, "4y+", "Expected expiry '%s' to result in duration of '4y+' but got '%s'" % (expiry,user_cert.duration_code))

    def test20_EventFile(self):
        '''
        Make sure that a Event file can be created
        '''
        self.assertIsNotNone(self.eventfile.date_created, "Expected UploadedFile.date_created to be populated.")
        self.assertEqual(self.eventfile.cabinet_id, self.cabinet_file.pk, "Expected cabinet to be %s but got %s" % (self.refile.cabinet, self.cabinet_file.pk))

        event_file = EventFile(
            event=self.event,
            file=self.eventfile
        )
        event_file.save()
        self.assertIsNotNone(event_file.date_created, "Expected UserRefFile.date_created to be populated.")
        self.assertEqual(event_file.file_id, self.eventfile.pk, "Expected user_file.file_id to be %s but got %s" % (event_file.file_id, self.refile.pk))
        self.assertEqual(event_file.event.title, self.event.title, "Expected user_file.event.title to be '%s' but got '%s" % (self.event.title, event_file.event.title))

        # Second user/file combination should raise integrity error
        event_file2 = EventFile(
            event=self.event,
            file=self.eventfile
        )
        self.assertRaises(IntegrityError, event_file2.save)




    def test50_UploadedFile_delete(self):
        '''
        Cascade delete from UploadedFile should work
        '''

        self.assertEqual(UploadedFile.objects.count(), 3, "Expected UploadedFile to have 3 entries but got '%d'." % ContactFile.objects.count())

        user_file = ContactRefFile.objects.create(
            contact=self.contact,
            file=self.refile
        )
        staff_file = ContactRefFile.objects.create(
            contact=self.staff_contact,
            file=self.refile
        )
        user_cert = ContactCertFile.objects.create(
            contact=self.contact,
            file=self.certfile,
            expiry=datetime.date(2012,7,10)
        )
        event_file = EventFile.objects.create(
            event=self.event,
            file=self.eventfile
        )

        self.assertEqual(ContactFile.objects.count(), 3, "Expected UserRefFile to have 3 entries but got '%d'." % ContactFile.objects.count())
        self.assertEqual(ContactRefFile.objects.count(), 2, "Expected UserRefFile to have 2 entries but got '%d'." % ContactRefFile.objects.count())
        self.assertEqual(ContactCertFile.objects.count(), 1, "Expected UserCertFile to have 1 entry but got '%d'." % ContactCertFile.objects.count())
        self.assertEqual(EventFile.objects.count(), 1, "Expected EventFile to have 1 entry but got '%d'." % EventFile.objects.count())

        for file in UploadedFile.objects.all():
             file.delete()

        self.assertEqual(ContactFile.objects.count(), 0, "Expected UserRefFile to have 0 entries but got '%d'." % ContactFile.objects.count())
        self.assertEqual(UploadedFile.objects.count(), 0, "Expected UploadedFile to have 0 entries but got '%d'." % UploadedFile.objects.count())
        self.assertEqual(ContactRefFile.objects.count(), 0, "Expected UserRefFile to have 0 entries but got '%d'." % ContactRefFile.objects.count())
        self.assertEqual(ContactCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry but got '%d'." % ContactCertFile.objects.count())
        self.assertEqual(EventFile.objects.count(), 0, "Expected EventFile to have 0 entry but got '%d'." % EventFile.objects.count())

    def test51_UserFile_delete(self):
        '''
        Cascade delete from EventFile, UserRefFile and UserCertFile should work up to UserFile but not UploadedFile
        '''

        self.assertEqual(UploadedFile.objects.count(), 3, "Expected UploadedFile to have 3 entries but got '%d'." % ContactFile.objects.count())

        user_file = ContactRefFile.objects.create(
            contact=self.contact,
            file=self.refile
        )
        staff_file = ContactRefFile.objects.create(
            contact=self.staff_contact,
            file=self.refile
        )
        user_cert = ContactCertFile.objects.create(
            contact=self.contact,
            file=self.certfile,
            expiry=datetime.date(2012,7,10)
        )
        event_file = EventFile.objects.create(
            event=self.event,
            file=self.eventfile
        )

        self.assertEqual(ContactFile.objects.count(), 3, "Expected UserRefFile to have 3 entries but got '%d'." % ContactFile.objects.count())
        self.assertEqual(ContactRefFile.objects.count(), 2, "Expected UserRefFile to have 2 entries but got '%d'." % ContactRefFile.objects.count())
        self.assertEqual(ContactCertFile.objects.count(), 1, "Expected UserCertFile to have 1 entry but got '%d'." % ContactCertFile.objects.count())
        self.assertEqual(EventFile.objects.count(), 1, "Expected EventFile to have 1 entry but got '%d'." % EventFile.objects.count())

        # Testing cascade delete for certificate file
        user_cert.delete()
        self.assertEqual(ContactFile.objects.count(), 2, "Expected UserRefFile to have 2 entries but got '%d'." % ContactFile.objects.count())
        self.assertEqual(UploadedFile.objects.count(), 3, "Expected UploadedFile to have 3 entries but got '%d'." % UploadedFile.objects.count())
        self.assertEqual(ContactRefFile.objects.count(), 2, "Expected UserRefFile to have 2 entries but got '%d'." % ContactRefFile.objects.count())
        self.assertEqual(ContactCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry but got '%d'." % ContactCertFile.objects.count())
        self.assertEqual(EventFile.objects.count(), 1, "Expected EventFile to have 1 entry but got '%d'." % EventFile.objects.count())

        # Testing cascade delete for reference file
        user_file.delete()
        self.assertEqual(ContactFile.objects.count(), 1, "Expected UserRefFile to have 1 entries but got '%d'." % ContactFile.objects.count())
        self.assertEqual(UploadedFile.objects.count(), 3, "Expected UploadedFile to have 3 entries but got '%d'." % UploadedFile.objects.count())
        self.assertEqual(ContactRefFile.objects.count(), 1, "Expected UserRefFile to have 1 entries but got '%d'." % ContactRefFile.objects.count())
        self.assertEqual(ContactCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry but got '%d'." % ContactCertFile.objects.count())
        self.assertEqual(EventFile.objects.count(), 1, "Expected EventFile to have 1 entry but got '%d'." % EventFile.objects.count())

        # Testing delete for event file
        event_file.delete()
        self.assertEqual(ContactFile.objects.count(), 1, "Expected UserRefFile to have 1 entries but got '%d'." % ContactFile.objects.count())
        self.assertEqual(UploadedFile.objects.count(), 3, "Expected UploadedFile to have 3 entries but got '%d'." % UploadedFile.objects.count())
        self.assertEqual(ContactRefFile.objects.count(), 1, "Expected UserRefFile to have 1 entries but got '%d'." % ContactRefFile.objects.count())
        self.assertEqual(ContactCertFile.objects.count(), 0, "Expected UserCertFile to have 0 entry but got '%d'." % ContactCertFile.objects.count())
        self.assertEqual(EventFile.objects.count(), 0, "Expected EventFile to have 0 entry but got '%d'." % EventFile.objects.count())


