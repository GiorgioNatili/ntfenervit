
import os
import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.forms import Form, ModelForm
from django import forms
from django.db import transaction
from django.forms.models import model_to_dict

from django.template.defaultfilters import slugify

from cabinet.models import UserFile, UploadedFile, UserRefFile, UserCertFile

'''
class UploadedFileForm(ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('title', 'cabinet', 'file_ref', 'owner')
class UserCertFileForm(ModelForm):
    class Meta:
        model = UserCertFile

UPLOAD_TO_DIR = "cabinet"

def upload_filename(instance, filename):
    date_subpath = datetime.date.today().strftime("%Y/%m/%d")
    fname, dot, extension = filename.rpartition('.')
    slug_filename = "%s.%s" % (slugify(fname), extension)
    return os.path.join(UPLOAD_TO_DIR, date_subpath, slug_filename)

class UploadedFileForm(forms.Form):
    title = forms.CharField(max_length=200, required=True)
    cabinet_id = forms.IntegerField()
    file_ref = forms.FileField(upload_to=upload_filename)
    owner_id = forms.IntegerField()

'''

class UploadedFileForm(ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('title', 'cabinet', 'file_ref', 'owner')

class UserRefFileForm(UploadedFileForm):
    user_id = forms.IntegerField()
    event_title = forms.CharField(required=False, label="Evento")
    class Meta(UploadedFileForm.Meta):
        pass

class UserCertFileForm(ModelForm):
    user_id = forms.IntegerField()
    expiry = forms.DateField(required=True, label="Scadenza", widget=forms.DateInput(format="%d/%m/%Y", attrs={'placeholder':'__/__/____'}))
    class Meta(UploadedFileForm.Meta):
        pass


def __view_user_file_common(**kwargs):
    '''
    Set up the view_user_file.html form status based on `file_type` and `action`
    '''
    # Setting based on Cabinate type: references or certificates
    if kwargs["file_type"] == "ref":
        kwargs["page_title"] = "Files"
        kwargs["cabinet_id"] = UserRefFile.CABINET_ID
        form_class = UserRefFileForm
        userfile_class = UserRefFile
        object_name = "file"
    else:
        kwargs["page_title"] = "Certificati"
        kwargs["cabinet_id"] = UserCertFile.CABINET_ID
        form_class = UserCertFileForm
        userfile_class = UserCertFile
        object_name = "certificato"

    # Setting based on action
    if kwargs["action"] == "add":
        kwargs["icon_name"] = "icon-plus"
        kwargs["page_subtitle"] = "Aggiungi un nuovo %s" % object_name
    else:
        kwargs["icon_name"] = "icon-file"
        kwargs["page_subtitle"] = "Visualizza e modifica gli attributi dell'%s selezionato" % object_name

    # Creating final output
    return {
        "form_class": form_class,
        "userfile_class": userfile_class,
        "data": kwargs
    }


def __view_user_file_set_form(pk_id, params):
    '''
    Set user form
    '''
    userfile = params["userfile_class"].objects.get(pk=pk_id)

    init_data = {}
    if params.data["file_type"] == "ref":
        if userfile.event:
            init_data["event_title"] = userfile.event.title
    else:
        init_data["expiry"] = userfile.expiry

    params.data["form"] = params["form_class"](initial=init_data,instance=userfile.file)

class ViewUserFileUtil(object):
    __data = {}
    def __init__(self, **kwargs):
        self.type = kwargs["file_type"]
        self.action = kwargs["action"]

        if self.type == "ref":
            self.form_class = UserRefFileForm
            self.userfile_class = UserRefFile
            self.object_name = "file"
            kwargs["page_title"] = "Files"
            kwargs["cabinet_id"] = UserRefFile.CABINET_ID
        else:
            self.form_class = UserCertFileForm
            self.userfile_class = UserCertFile
            self.object_name = "certificato"
            kwargs["page_title"] = "Certificati"
            kwargs["cabinet_id"] = UserCertFile.CABINET_ID

        # Setting based on action
        if self.action == "add":
            kwargs["icon_name"] = "icon-plus"
            kwargs["page_subtitle"] = "Aggiungi un nuovo %s" % self.object_name
        else:
            kwargs["icon_name"] = "icon-file"
            kwargs["page_subtitle"] = "Visualizza e modifica gli attributi dell'%s selezionato" % self.object_name

        # set data
        self.__data = kwargs

    def set_form(self, pk_id=None):
        if self.action == "add":
            self.__data["form"] = self.form_class()
        else:
            user_file = self.userfile_class.objects.get(pk=pk_id)
            init_data = {}
            if self.type == "ref":
                if user_file.event and user_file.event.title:
                    init_data["event_title"] = user_file.event.title
                else:
                    init_data["event_title"] = " "
            else:
                init_data["expiry"] = user_file.expiry

            self.__data["form"] = self.form_class(initial=init_data,instance=user_file.file)

    def save_form(self, file, post):
        if self.type == "ref":
            ufile_object = UserRefFile(user_id=self.data["user_id"], file=file)
        else:
            dt = post.get("expiry")
            ufile_object = UserCertFile(user_id=self.data["user_id"], file=file, expiry=datetime.datetime.strptime(dt, "%d/%m/%Y"))
        ufile_object.save()
        return HttpResponseRedirect(post.get("referer"))

    def _get_data(self):
        return self.__data
    data = property(_get_data)

@user_passes_test(lambda u:u.is_superuser)
def view_user_file_add(request, user_id, type):
    util = ViewUserFileUtil(
        action="add",
        file_type=type,
        user_id=user_id,
        owner_id=request.user.id,
        referer = request.META.get('HTTP_REFERER')
    )

    if request.method == "POST":
        form = util.form_class(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            return util.save_form(file, request.POST)
        else:
            print "uploaded_pform error: %s" % form.errors
            util.data["form"] = form
            return render_to_response('admin/cabinet/view_user_file.html', util.data, context_instance=RequestContext(request))

    else:
        util.set_form()

        #file = UploadedFile(title=data.get("title"), cabinet_id=data.get("cabinet_id"), file_ref = request.FILES['file_ref'], owner=request.user)
        #file.save()
        return render_to_response('admin/cabinet/view_user_file.html', util.data, context_instance=RequestContext(request))

@user_passes_test(lambda u:u.is_superuser)
def view_user_file(request, user_id, type, id):
    util = ViewUserFileUtil(
        action="edit",
        file_type=type,
        user_id=user_id,
        file_id=id,
        owner_id=request.user.id,
        referer=request.META.get('HTTP_REFERER'))

    if request.method == "POST":
        user_file = get_object_or_404(util.userfile_class, id=id)
        upload_file = user_file.file
        if request.POST.get("action") == "save":
            form = util.form_class(request.POST, request.FILES, instance=upload_file)
            print "view_user_file called.  File: %s" % request.FILES

            if 'file_ref' in request.FILES:
                # File Changed
                # form = util.form_class(request.POST, request.FILES)
                file_ref = request.FILES['file_ref']
                if form.is_valid():
                    file = form.save()
                    if type == "cert":
                        dt = datetime.datetime.strptime(form['expiry'].value(), "%d/%m/%Y")
                        user_file.expiry = dt
                        user_file.save()

                    return HttpResponseRedirect(request.POST.get('referer'))
                else:
                    print "uploaded_pform error: %s" % form.errors
                    util.data["form"] = form
                    return render_to_response('admin/cabinet/view_user_file.html', util.data, context_instance=RequestContext(request))
            else:
                print "### File not changed, title: %s" % form['title'].value()

                # Update all field except file
                if type == "cert":
                    dt = datetime.datetime.strptime(form['expiry'].value(), "%d/%m/%Y")
                    user_file.expiry = dt

                upload_file.title = form['title'].value()
                user_file.save()
                upload_file.save()

                return HttpResponseRedirect(request.POST.get('referer'))
        else:
            upload_delete = False
            if UserFile.objects.filter(file=upload_file).exists():
                file_fullpath = upload_file.file_fullpath()
                upload_delete = True

            user_file.delete()
            if upload_delete:
                print "### File deleted!!!"
                upload_file.delete()
                os.remove(file_fullpath)

            return HttpResponseRedirect(request.POST.get('referer'))
    else:
        util.set_form(id)

    return render_to_response('admin/cabinet/view_user_file.html', util.data, context_instance=RequestContext(request))
