from haystack import indexes
from contacts.models import Contact
from cabinet.models import UserCertFile


class UserCertFileIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    expiry = indexes.DateField(model_attr='expiry')
    duration = indexes.IntegerField(model_attr="duration")
    duration_code = indexes.CharField(model_attr="duration_code")
    is_valid = indexes.BooleanField(model_attr='is_valid')

    user_id = indexes.IntegerField()
    title = indexes.CharField()
    name = indexes.CharField()
    email = indexes.CharField()
    cert_file_id = indexes.IntegerField()
    file_url = indexes.CharField()
    file_name = indexes.CharField()

    def get_model(self):
        return UserCertFile

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.all()

    def prepare(self, object):
        self.prepared_data = super(UserCertFileIndex, self).prepare(object)

        # Append the contact detail to the end of the text
        # ToDo: Ideally, the UserFile object should modified to contain `contact` instead of `user`, making contact lookup below unecessary
        contact = Contact.objects.get(owner=object.user)
        if contact:
            self.prepared_data['user_id'] = object.user.id
            self.prepared_data['title'] = object.file.title
            self.prepared_data['name'] = "%s %s" % (contact.name, contact.surname)
            self.prepared_data['email'] = contact.email
            self.prepared_data['cert_file_id'] = object.pk
            self.prepared_data['file_url'] = object.file.file_ref.url
            self.prepared_data['file_name'] = object.file.file_basename()
            # self.prepared_data["duration_code"] = object.duration_code

            contact_text = "\n".join([
                contact.code,
                self.prepared_data['name'],
                self.prepared_data['email'],
                contact.city,
                self.prepared_data['title'],
                self.prepared_data['file_name'],
                object.expiry.strftime("%d-%m-%Y")
            ])

            self.prepared_data['text'] = contact_text
            #print "### prepared_data: %s" % self.prepared_data['text']

        return self.prepared_data