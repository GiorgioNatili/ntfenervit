from haystack.forms import SearchForm,ModelSearchForm, HighlightedModelSearchForm
from django import forms


class CampaignSearchForm(HighlightedModelSearchForm):
    name = forms.CharField(max_length=100,required=False)
    description = forms.CharField(max_length=100,required=False)
    startdate = forms.DateField(required=False)
    enddate = forms.DateField(required=False)
    status = forms.CharField(max_length=100,required=False)

    def no_query_found(self):
        return self.searchqueryset

    def search(self):
        sqs = super(CampaignSearchForm,self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['name']:
            sqs = sqs.filter(content = self.cleaned_data["name"])
        if self.cleaned_data['description']:
            sqs = sqs.filter(content = self.cleaned_data['description'])
        if self.cleaned_data['status']:
            sqs = sqs.filter(content = self.cleaned_data['status'])
        if self.cleaned_data['startdate']:
            sqs = sqs.filter(content = self.cleaned_data['startdate'])
        if self.cleaned_data['enddate']:
            sqs = sqs.filter(content = self.cleaned_data['enddate'])

        return sqs


class NewsletterSearchForm(HighlightedModelSearchForm):
    name = forms.CharField(max_length=100,required=False)
    description = forms.CharField(max_length=100,required=False)
    startdate = forms.DateField(required=False)
    enddate = forms.DateField(required=False)
    status = forms.CharField(max_length=100,required=False)
    campaign = forms.CharField(max_length=100,required=False)
    event = forms.CharField(max_length=100,required=False)

    def no_query_found(self):
        return self.searchqueryset

    def search(self):
        sqs = super(NewsletterSearchForm,self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['name']:
            sqs = sqs.filter(content = self.cleaned_data["name"])
        if self.cleaned_data['description']:
            sqs = sqs.filter(content = self.cleaned_data['description'])
        if self.cleaned_data['status']:
            sqs = sqs.filter(content = self.cleaned_data['status'])
        if self.cleaned_data['campaign']:
            sqs = sqs.filter(content = self.cleaned_data['campaign'])
        if self.cleaned_data['event']:
            sqs = sqs.filter(content = self.cleaned_data['event'])
        return sqs


class EventSearchForm(HighlightedModelSearchForm):
    title = forms.CharField(max_length=100,required=False)
    place = forms.CharField(max_length=100,required=False)
    date = forms.DateField(required=False)
    campaign = forms.CharField(max_length=100,required=False)
    province = forms.CharField(max_length=100,required=False)
    enddate = forms.DateField(required=False)
    status = forms.CharField(max_length=100,required=False)
    pointofsale = forms.CharField(max_length=100,required=False)
    pointofsaletype = forms.CharField(max_length=100,required=False)
    pointofsaledescription = forms.CharField(max_length=100,required=False)
    areamanager = forms.CharField(max_length=100,required=False)
    typepointofsale = forms.CharField(max_length=100,required=False)
    its_districtmanager = forms.CharField(max_length=100,required=False)
    consultant = forms.CharField(max_length=100, required=False)
    district = forms.CharField(max_length=100,required=False)
    channel = forms.CharField(max_length=100,required=False)
    eventtype = forms.CharField(max_length=100,required=False)
    theme = forms.CharField(max_length=100,required=False)
    trainer = forms.CharField(max_length=100,required=False)

    def no_query_found(self):
        return self.searchqueryset

    def search(self):
        sqs = super(EventSearchForm, self).search()
        # print(str(sqs))
        if not self.is_valid():
            return self.no_query_found()
        for _ in ('title', 'place', 'campaign', 'province',
                  'status', 'pointofsaletype', 'pointofsaledescription', 'areamanager',
                  'typepointofsale', 'its_districtmanager', 'district', 'consultant',
                  'channel', 'eventtype', 'theme', 'trainer'):
            if self.cleaned_data[_]:
                sqs = sqs.filter(content=self.cleaned_data[_])
		
        if self.cleaned_data["date"]:
            sqs = sqs.filter(date__gte=self.cleaned_data["date"])
        if self.cleaned_data["enddate"]:
            sqs = sqs.filter(date__lte=self.cleaned_data["enddate"])

        return sqs