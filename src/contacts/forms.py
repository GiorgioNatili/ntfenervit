from haystack.forms import SearchForm,ModelSearchForm, HighlightedModelSearchForm
from django import forms

class ContactSearchForm(HighlightedModelSearchForm):
    name = forms.CharField(max_length=100,required=False)
    surname = forms.CharField(max_length=100,required=False)
    work = forms.CharField(max_length=100,required=False)
    province =  forms.CharField(max_length=100,required=False)
    status = forms.CharField(max_length=100,required=False)
    sex =  forms.CharField(max_length=100,required=False)
    city =  forms.CharField(max_length=100,required=False)
    street =  forms.CharField(max_length=100,required=False)
    zip =  forms.CharField(max_length=100,required=False)


    def no_query_found(self):
        return self.searchqueryset

    def search(self):
        sqs = super(ContactSearchForm,self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['name']:
            sqs = sqs.filter(content = self.cleaned_data["name"])
        if self.cleaned_data['surname']:
            sqs = sqs.filter(content = self.cleaned_data['surname'])
        if self.cleaned_data['work']:
            sqs = sqs.filter(content = self.cleaned_data['work'])
        if self.cleaned_data['province']:
            sqs = sqs.filter(content = self.cleaned_data['province'])
        if self.cleaned_data['status']:
            sqs = sqs.filter(content = self.cleaned_data['status'])
        if self.cleaned_data['sex']:
            sqs = sqs.filter(content = self.cleaned_data['sex'])
        if self.cleaned_data['city']:
            sqs = sqs.filter(content = self.cleaned_data['city'])
        if self.cleaned_data['street']:
            sqs = sqs.filter(content = self.cleaned_data['street'])
        if self.cleaned_data['zip']:
            sqs = sqs.filter(content = self.cleaned_data['zip'])

        #sqs = sqs.order_by(title)



        return sqs



