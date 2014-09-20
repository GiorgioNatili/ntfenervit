from haystack import indexes
from campaigns.models import Campaign, Event, Newsletter

class AllCampaignIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    class Meta:
        model = Campaign

class AllEventIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    class Meta:
        model = Event

class AllNewsletterIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    class Meta:
        model = Newsletter



