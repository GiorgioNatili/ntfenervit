'''
Model for keeping track of uploaded files
'''

import os
import datetime
from dateutil.relativedelta import relativedelta

from django.db import IntegrityError
from django.template.defaultfilters import slugify

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from contacts.models import Contact
from campaigns.models import Event

UPLOAD_TO_DIR = "cabinet"


class Cabinet(models.Model):
    '''
    File type to store.  1 = Reference, 2 = Certificates
    '''
    cabinet_name = models.CharField(max_length=200, blank=False)

def upload_filename(instance, filename):
    date_subpath = datetime.date.today().strftime("%Y/%m/%d")
    fname, dot, extension = filename.rpartition('.')
    slug_filename = "%s.%s" % (slugify(fname), extension)
    return os.path.join(UPLOAD_TO_DIR, date_subpath, slug_filename)

class UploadedFile(models.Model):
    '''
    UploadedFile is repository of files. There is one entry per file
    '''
    title = models.CharField(max_length=200, blank=False, verbose_name="Titolo")
    cabinet = models.ForeignKey(Cabinet)
    file_ref = models.FileField(upload_to=upload_filename, blank=False, verbose_name="Allegata file")
    owner = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def file_basename(self):
        if self.file_ref:
            return os.path.basename(self.file_ref.name)

    @property
    def file_fullpath(self):
        if self.file_ref:
            return os.path.join(settings.MEDIA_ROOT, self.file_ref.name)

class EventFile(models.Model):
    CABINET_ID = 1
    event = models.ForeignKey(Event, blank=True, null=True)
    file = models.ForeignKey(UploadedFile)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("event", "file"),)

    def save(self, *args, **kwargs):
        '''
        Overriding the save perform file cabinet validation.
        '''

        if self.file.cabinet_id == self.CABINET_ID:
            super(EventFile, self).save(*args, **kwargs)
        else:
            raise IntegrityError("Only cabinet_id '%d' allowed but got '%d'" % (self.CABINET_ID, self.file.cabinet_id))


class ContactFile(models.Model):
    CABINET_ID = 0
    contact = models.ForeignKey(Contact)
    file = models.ForeignKey(UploadedFile)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("contact", "file"),)

    def save(self, *args, **kwargs):
        '''
        Overriding the save perform file cabinet validation.
        '''

        if self.file.cabinet_id == self.CABINET_ID:
            super(ContactFile, self).save(*args, **kwargs)
        else:
            raise IntegrityError("Only cabinet_id '%d' allowed but got '%d'" % (self.CABINET_ID, self.file.cabinet_id))


'''
2014-07-22: ContactRefFile.event is suppressed in the front end following introduction of EventFile object.
            It has not been removed from the data model intentionally, awaiting further decision from users.
'''
class ContactRefFile(ContactFile):
    CABINET_ID = 1
    event = models.ForeignKey(Event, blank=True, null=True)

class ContactCertFile(ContactFile):
    CABINET_ID = 2
    expiry = models.DateField(blank=False)

    @property
    def is_valid(self):
        if self.expiry:
            return self.expiry >= datetime.date.today()
        else:
            return False

    @property
    def duration(self):
        """
        Return duration in years
        :return: integer, -1 for invalid certificate
        """
        if self.is_valid:
            return relativedelta(self.expiry, datetime.date.today()).years
        else:
            return -1

    @property
    def duration_code(self):
        """
        Return following code:
        expired: duration = -1
        1y-:      duration = 0 or 1
        2y:       duration = 2
        3y:       duration = 3
        4y+:      duration >= 4
        :return: string
        """
        duration = self.duration
        if duration == -1:
            return "expired"
        elif duration <= 1:
            return "1y-"
        elif duration == 2:
            return "2y"
        elif duration == 3:
            return "3y"
        else:
            return "4y+"



