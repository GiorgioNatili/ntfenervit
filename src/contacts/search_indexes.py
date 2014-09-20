from haystack import indexes
from contacts.models import Contact

class AllContactIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    class Meta:
        model = Contact



