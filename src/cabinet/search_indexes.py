from haystack import indexes
from django.core.exceptions import ObjectDoesNotExist
from contacts.models import Contact
from cabinet.models import ContactCertFile


class UserCertFileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    expiry = indexes.DateField(model_attr='expiry')
    duration = indexes.IntegerField(model_attr="duration")
    duration_code = indexes.CharField(model_attr="duration_code")
    is_valid = indexes.BooleanField(model_attr='is_valid')
    contact = indexes.CharField(model_attr="contact")

    title = indexes.CharField()
    name = indexes.CharField()
    email = indexes.CharField()
    cert_file_id = indexes.IntegerField()
    file_url = indexes.CharField()
    file_name = indexes.CharField()

    def get_model(self):
        return ContactCertFile

    def prepare(self, object):
        self.prepared_data = super(UserCertFileIndex, self).prepare(object)

        # self.prepared_data['user_id'] = object.user.id
        self.prepared_data['title'] = object.file.title
        self.prepared_data['name'] = "%s %s" % (object.contact.name, object.contact.surname)
        self.prepared_data['email'] = object.contact.email
        self.prepared_data['cert_file_id'] = object.pk
        self.prepared_data['file_url'] = object.file.file_ref.url
        self.prepared_data['file_name'] = object.file.file_basename

        return self.prepared_data