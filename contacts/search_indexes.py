from haystack import indexes
from contacts.models import Contact

class AllContactIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = Contact



