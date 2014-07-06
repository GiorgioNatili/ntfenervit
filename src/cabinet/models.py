'''
Model for keeping track of uploaded files
'''

import os
import datetime

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

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
    file_ref = models.FileField(upload_to=upload_filename, verbose_name="Allegata file")
    owner = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)

    def file_basename(self):
        if self.file_ref:
            return os.path.basename(self.file_ref.name)

    def file_fullpath(self):
        if self.file_ref:
            return os.path.join(settings.MEDIA_ROOT, self.file_ref.name)


class UserFile(models.Model):
    CABINET_ID = 0
    user = models.ForeignKey(User)
    file = models.ForeignKey(UploadedFile)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "file"),)

    def save(self, *args, **kwargs):
        '''
        Overriding the save perform file cabinet validation.
        '''

        if self.file.cabinet_id == self.CABINET_ID:
            super(UserFile, self).save(*args, **kwargs)
        else:
            raise IntegrityError("Only cabinet_id '%d' allowed but got '%d'" % (self.CABINET_ID, self.file.cabinet_id))



class UserRefFile(UserFile):
    CABINET_ID = 1
    event = models.ForeignKey(Event, blank=True, null=True)

class UserCertFile(UserFile):
    CABINET_ID = 2
    expiry = models.DateField()

