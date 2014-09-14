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

        #sqs = sqs.order_by(title)
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
        sqs = super(EventSearchForm,self).search()

        if not self.is_valid():
            return self.no_query_found()
        for field in ('its_district_manager', 'district', 'consultant'):
            if self.cleaned_data[field] and self.cleaned_data[field] == '-1':
                self.cleaned_data[field] = ""
        if self.cleaned_data['title']:
            sqs = sqs.filter(content = self.cleaned_data["title"])
        if self.cleaned_data['place']:
            sqs = sqs.filter(content = self.cleaned_data['place'])
        if self.cleaned_data['date']:
            sqs = sqs.filter(content = self.cleaned_data['date'])
        if self.cleaned_data['campaign']:
            sqs = sqs.filter(content = self.cleaned_data['campaign'])
        if self.cleaned_data['province']:
            sqs = sqs.filter(content = self.cleaned_data['province'])
        if self.cleaned_data['enddate']:
            sqs = sqs.filter(content = self.cleaned_data['enddate'])
        if self.cleaned_data['status']:
            sqs = sqs.filter(content = self.cleaned_data['status'])
        if self.cleaned_data['pointofsale']:
            sqs = sqs.filter(content = self.cleaned_data['pointofsale'])
        if self.cleaned_data['pointofsaletype']:
            sqs = sqs.filter(content = self.cleaned_data['pointofsaletype'])
        if self.cleaned_data['pointofsaledescription']:
            sqs = sqs.filter(content = self.cleaned_data['pointofsaledescription'])
        if self.cleaned_data['areamanager']:
            sqs = sqs.filter(content = self.cleaned_data['areamanager'])
        if self.cleaned_data['typepointofsale']:
            sqs = sqs.filter(content = self.cleaned_data['typepointofsale'])
        if self.cleaned_data['its_districtmanager']:
            sqs = sqs.filter(content = self.cleaned_data['its_districtmanager'])
        if self.cleaned_data['district']:
            sqs = sqs.filter(content = self.cleaned_data['district'])
        if self.cleaned_data['consultant']:
            sqs = sqs.filter(content=self.cleaned_data['consultant'])
        if self.cleaned_data['channel']:
            sqs = sqs.filter(content = self.cleaned_data['channel'])
        if self.cleaned_data['eventtype']:
            sqs = sqs.filter(content = self.cleaned_data['eventtype'])
        if self.cleaned_data['theme']:
            sqs = sqs.filter(content = self.cleaned_data['theme'])
        if self.cleaned_data['trainer']:
            sqs = sqs.filter(content = self.cleaned_data['trainer'])
        return sqs