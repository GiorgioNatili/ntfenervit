'''
Model for keeping track of uploaded files
'''

from django.db import models
from django.contrib.auth.models import User

from django.db import IntegrityError
from django.core.exceptions import ValidationError

from campaigns.models import Event

UPLOAD_TO_DIR = "cabinet/%Y/%m/%d/"


class Cabinet(models.Model):
    '''
    File type to store.  1 = Reference, 2 = Certificates
    '''
    cabinet_name = models.CharField(max_length=200, blank=False)


class UploadedFile(models.Model):
    '''
    UploadedFile is repository of files. There is one entry per file
    '''
    title = models.CharField(max_length=200, blank=False)
    cabinet = models.ForeignKey(Cabinet)
    file_ref = models.FileField(upload_to=UPLOAD_TO_DIR)
    owner = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)

class UserFile(models.Model):
    user = models.ForeignKey(User)
    file = models.ForeignKey(UploadedFile)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "file"),)

    def save(self, *args, **kwargs):
        '''
        Overriding the save to call clean.
        '''
        # ToDo: Find a better way to do a model validation.  When used with ModelForm, .full_clean() is gonna be called twice

        # Translate ValidationError to IntegrityError
        try:
            self.clean()
        except ValidationError as e:
            raise IntegrityError(e)

        super(UserFile, self).save(*args, **kwargs)


class UserRefFile(UserFile):
    CABINET_REFERENCE = 1
    event = models.ForeignKey(Event, blank=True, null=True)

    def clean(self):
        '''
        Validate Model so that only files from References Cabinet allowed.
        '''
        if self.file.cabinet_id != 1:
            raise ValidationError("Only entries with Cabinet type 'References[1]' allowed.  Got Cabinet '%s'" % self.file.cabinet_id)

class UserCertFile(UserFile):
    CABINET_CERTIFICATE = 2
    expiry = models.DateField()

    def clean(self):
        if self.file.cabinet_id != 2:
            raise ValidationError("Only entries with Cabinet type 'Certificates[2]' allowed.  Got Cabinet '%s'" % self.file.cabinet_id)
