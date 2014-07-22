
import os
import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import SuspiciousOperation
from django.core.exceptions import ValidationError
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.forms import Form, ModelForm
from django import forms
from haystack.forms import ModelSearchForm

from cabinet.models import UploadedFile, ContactFile, EventFile, ContactRefFile, ContactCertFile

class UploadedFileForm(ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('title', 'cabinet', 'file_ref', 'owner')

    def clean(self):
        if self.cleaned_data:
            file_ref = self.cleaned_data.get("file_ref")
            if file_ref:
                name, ext = os.path.splitext(file_ref.name)
                if ext.lower() not in self.ALLOWED_EXTS:
                    raise ValidationError("File con estensione '%s' non supportato." % ext)

        return self.cleaned_data


class UserRefFileForm(UploadedFileForm):
    ALLOWED_EXTS = frozenset(['.ppt', '.pptx', '.pps', '.ppsx', '.doc', '.docx', '.pdf', '.tif', '.tiff', '.png'])
    contact_id = forms.CharField(max_length=16)
    event_title = forms.CharField(required=False, label="Evento")
    class Meta(UploadedFileForm.Meta):
        pass

class UserCertFileForm(UploadedFileForm):
    ALLOWED_EXTS = frozenset(['.pdf', '.tif', '.tiff', '.png'])
    contact_id = forms.CharField(max_length=16)
    expiry = forms.DateField(required=True, label="Scadenza", widget=forms.DateInput(format="%d/%m/%Y", attrs={'placeholder':'__/__/____'}))
    class Meta(UploadedFileForm.Meta):
        pass

class EventFileForm(UploadedFileForm):
    ALLOWED_EXTS = frozenset(['.ppt', '.pptx', '.pps', '.ppsx', '.doc', '.docx', '.pdf', '.tif', '.tiff', '.png'])
    class Meta(UploadedFileForm.Meta):
        pass



class ViewUserFileUtil(object):
    """
    An utility class to manage different action and state of the view
    """
    __data = {}
    def __init__(self, **kwargs):
        self.type = kwargs["file_type"]
        self.action = kwargs["action"]

        if self.type == "ref":
            self.form_class = UserRefFileForm
            self.userfile_class = ContactRefFile
            self.object_name = "file"
            kwargs["contact_id"] = kwargs["entity_id"]
            kwargs["page_title"] = "Files"
            kwargs["cabinet_id"] = ContactRefFile.CABINET_ID
        elif self.type == "cert":
            self.form_class = UserCertFileForm
            self.userfile_class = ContactCertFile
            self.object_name = "certificato"
            kwargs["contact_id"] = kwargs["entity_id"]
            kwargs["page_title"] = "Certificati"
            kwargs["cabinet_id"] = ContactCertFile.CABINET_ID
        elif self.type == "event":
            self.form_class = EventFileForm
            self.userfile_class = EventFile
            self.object_name = "file"
            kwargs["event_id"] = kwargs["entity_id"]
            kwargs["page_title"] = "Files per Evento"
            kwargs["cabinet_id"] = EventFile.CABINET_ID
        else:
            raise RuntimeError("Type of '%s' used in cabinet.view not supported." % self.type)

        # Remove the generic entity_id entry now that contact_id or event_id has been set
        del kwargs["entity_id"]

        # Setting based on action
        if self.action == "add":
            kwargs["icon_name"] = "icon-plus"
            kwargs["page_subtitle"] = "Aggiungi un nuovo %s" % self.object_name
        else:
            kwargs["icon_name"] = "icon-file"
            kwargs["page_subtitle"] = "Visualizza e modifica gli attributi dell'%s selezionato" % self.object_name

        # set data
        self.__data = kwargs

    def get_redirect_response(self, post, get=None):
        # Check if hash query string has been passed
        if get:
            hash = get.get("hash")
        else:
            hash = None

        # Build the url with hash if provided
        if post.get("referer"):
            if hash:
                url = "%s#%s" % (post.get("referer"), hash)
            else:
                url = post.get("referer")
        elif post.get("contact_id"):
            url = "/admin/contacts/contact/%s/#filesTab" % post.get("contact_id")
        elif post.get("event_id"):
            url = "/admin/campaigns/event/%d/" % post.get("event_id")
        else:
            if self.type == "event":
                url = "/admin/campaigns/event/"
            else:
                url = "/admin/backend/utenti/"
        return HttpResponseRedirect(url)

    def initialize_form(self, pk_id=None):
        if self.action == "add":
            self.__data["form"] = self.form_class()
        else:
            contact_file = self.userfile_class.objects.get(pk=pk_id)
            init_data = {}
            if self.type == "ref":
                if contact_file.event and contact_file.event.title:
                    init_data["event_title"] = contact_file.event.title
                else:
                    init_data["event_title"] = " "
            elif self.type == "cert":
                init_data["expiry"] = contact_file.expiry
            else:
                pass

            self.__data["form"] = self.form_class(initial=init_data,instance=contact_file.file)

    def save_user_form(self, form, post, get, contact_file=None):
        """
        Action to be called after form.save() has been called
        :param form:  Form to be saved
        :param post: request.POST object
        :param contact_file: instance of contact_file
        :return: HttpResponseRedirect
        """
        file_ref = form.save()

        if not contact_file:
            contact_file = self.userfile_class(contact_id=self.data["contact_id"], file=file_ref)

        if self.type == "cert":
            dt = form['expiry'].value()
            contact_file.expiry = datetime.datetime.strptime(dt, "%d/%m/%Y")

        contact_file.save()

        return self.get_redirect_response(post, get)

    def save_event_form(self, form, post, get, event_file=None):
        """
        Action to be called after form.save() has been called
        :param form:  Form to be saved
        :param post: request.POST object
        :param contact_file: instance of contact_file
        :return: HttpResponseRedirect
        """
        file_ref = form.save()

        if not event_file:
            event_file = self.userfile_class(event_id=self.data["event_id"], file=file_ref)

        event_file.save()

        return self.get_redirect_response(post, get)

    def _get_data(self):
        return self.__data
    data = property(_get_data)


def ViewUserFileAdd(request, entity_id, type):
    """
    Method to be called by the method bound to the edit url methods, allowing for different
    permssion depending on the file type
    """
    util = ViewUserFileUtil(
        action="add",
        file_type=type,
        entity_id=entity_id,
        owner_id=request.user.id,
        referer = request.META.get('HTTP_REFERER')
    )

    if request.method == "POST":
        form = util.form_class(request.POST, request.FILES)
        if form.is_valid():
            if util.type == "event":
                return util.save_event_form(form, request.POST, request.GET)
            else:
                return util.save_user_form(form, request.POST, request.GET)
        else:
            util.data["form"] = form
            return render_to_response('admin/cabinet/view_contact_file.html', util.data, context_instance=RequestContext(request))

    else:
        util.initialize_form()
        return render_to_response('admin/cabinet/view_contact_file.html', util.data, context_instance=RequestContext(request))

def ViewUserFile(request, entity_id, type, id):
    """
    Method to be called by the method bound to the edit url methods, allowing for different
    permssion depending on the file type
    """
    util = ViewUserFileUtil(
        action="edit",
        file_type=type,
        entity_id=entity_id,
        file_id=id,
        owner_id=request.user.id,
        referer=request.META.get('HTTP_REFERER'))

    if request.method == "POST":
        file_entry = get_object_or_404(util.userfile_class, id=id)
        upload_file = file_entry.file

        # Procesisng post according to action
        if request.POST.get("action") == "edit":
            form = util.form_class(request.POST, request.FILES, instance=upload_file)

            # File has been changed
            if 'file_ref' in request.FILES:
                file_ref = request.FILES['file_ref']
                if form.is_valid():
                    return util.save_user_form(form, request.POST, request.GET, file_entry)
                else:
                    util.data["form"] = form
                    return render_to_response('admin/cabinet/view_contact_file.html', util.data, context_instance=RequestContext(request))
            else:
                # File not changed.  Cannot user form save as it will not validate due to missing file_ref field.
                # Using the models directly

                # Update all field except file
                if type == "cert":
                    dt = form['expiry'].value()
                    file_entry.expiry = datetime.datetime.strptime(dt, "%d/%m/%Y")

                upload_file.title = form['title'].value()
                file_entry.save()
                upload_file.save()
                return util.get_redirect_response(request.POST, request.GET)

        elif request.POST.get("action") == "delete":
            upload_delete = False

            if type == "event":
                if EventFile.objects.filter(file=upload_file).count() == 1:
                    file_fullpath = upload_file.file_fullpath
                    upload_delete = True
            else:
                if ContactFile.objects.filter(file=upload_file).count() == 1:
                    file_fullpath = upload_file.file_fullpath
                    upload_delete = True

            file_entry.delete()
            if upload_delete:
                upload_file.delete()
                os.remove(file_fullpath)

            return util.get_redirect_response(request.POST, request.GET)
        else:
            raise SuspiciousOperation("Unexpected form action '%s' received" % request.POST.get("action"))
    else:
        util.initialize_form(id)

    return render_to_response('admin/cabinet/view_contact_file.html', util.data, context_instance=RequestContext(request))


@staff_member_required
def view_contact_file_add(request, contact_id, type):
    return ViewUserFileAdd(request, contact_id, type)

@staff_member_required
def view_contact_file(request, contact_id, type, id):
    return ViewUserFile(request, contact_id, type, id)

@staff_member_required
def view_event_file_add(request, event_id):
    return ViewUserFileAdd(request, event_id, type)

@staff_member_required
def view_event_file(request, event_id, id):
    return ViewUserFile(request, event_id, type, id)


'''
SEARCH
'''
class CertSearchForm(ModelSearchForm):
    title = forms.CharField(max_length=100,required=False)
    duration_code = forms.CharField(max_length=10, required=False)

    def no_query_found(self):
        return self.searchqueryset

    def search(self):
        sqs = super(CertSearchForm,self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['title']:
            sqs = sqs.filter(title__startswith = self.cleaned_data['title'])
        if self.cleaned_data['duration_code']:
            sqs = sqs.filter(duration_code = self.cleaned_data['duration_code'])
        return sqs

def search_certificate(request):
    form = CertSearchForm(request.GET)
    result_ids = set()
    results = []
    if request.GET.has_key('q'):
        res = form.search()
        for entry in res:
            #print "### Certificate Entry Found: %s" % entry
            if entry and entry.pk not in result_ids:
                result_ids.add(entry.pk)
                results.append(entry)
                # print "### Certificate Entry Found: %s" % entry
    #print "### Search Results: %s" % results

    return render_to_response(
        "admin/search/search_certificate.html",
        {
            'form': form,
            'results': results,
            'search_model': 'cabinet.contactcertfile'
        },
        context_instance=RequestContext(request)
    )