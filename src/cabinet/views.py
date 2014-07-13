
import os
import datetime

from django.core.exceptions import SuspiciousOperation
from django.core.exceptions import ValidationError
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.forms import Form, ModelForm
from django import forms

from cabinet.models import UserFile, UploadedFile, UserRefFile, UserCertFile

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
    user_id = forms.IntegerField()
    event_title = forms.CharField(required=False, label="Evento")
    class Meta(UploadedFileForm.Meta):
        pass

class UserCertFileForm(UploadedFileForm):
    ALLOWED_EXTS = frozenset(['.pdf', '.tif', '.tiff', '.png'])
    user_id = forms.IntegerField()
    expiry = forms.DateField(required=True, label="Scadenza", widget=forms.DateInput(format="%d/%m/%Y", attrs={'placeholder':'__/__/____'}))
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

    def get_redirect_response(self, post):
        if post.get("referer"):
            url = post.get("referer")
        elif post.get("user_id"):
            url = "/admin/backend/utenti/details/%d/" % post.get("user_id")
        else:
            url = "/admin/backend/utenti/"
        return HttpResponseRedirect(url)

    def initialize_form(self, pk_id=None):
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

    def save_form(self, form, post, user_file=None):
        """
        Action to be called after form.save() has been called
        :param form:  Form to be saved
        :param post: request.POST object
        :param user_file: instance of user_file
        :return: HttpResponseRedirect
        """
        file_ref = form.save()

        if not user_file:
            user_file = self.userfile_class(user_id=self.data["user_id"], file=file_ref)

        if self.type == "cert":
            dt = form['expiry'].value()
            user_file.expiry = datetime.datetime.strptime(dt, "%d/%m/%Y")

        user_file.save()

        return self.get_redirect_response(post)

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
            return util.save_form(form, request.POST)
        else:
            util.data["form"] = form
            return render_to_response('admin/cabinet/view_user_file.html', util.data, context_instance=RequestContext(request))

    else:
        util.initialize_form()

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
        if request.POST.get("action") == "edit":
            form = util.form_class(request.POST, request.FILES, instance=upload_file)

            # File has been changed
            if 'file_ref' in request.FILES:
                file_ref = request.FILES['file_ref']
                if form.is_valid():
                    return util.save_form(form,request.POST,user_file)
                else:
                    util.data["form"] = form
                    return render_to_response('admin/cabinet/view_user_file.html', util.data, context_instance=RequestContext(request))
            else:
                # File not changed.  Cannot user form save as it will not validate due to missing file_ref field.
                # Using the models directly

                # Update all field except file
                if type == "cert":
                    dt = form['expiry'].value()
                    user_file.expiry = datetime.datetime.strptime(dt, "%d/%m/%Y")

                upload_file.title = form['title'].value()
                user_file.save()
                upload_file.save()
                return util.get_redirect_response(request.POST)

        elif request.POST.get("action") == "delete":
            upload_delete = False
            if UserFile.objects.filter(file=upload_file).exists():
                file_fullpath = upload_file.file_fullpath()
                upload_delete = True

            user_file.delete()
            if upload_delete:
                upload_file.delete()
                os.remove(file_fullpath)

            return util.get_redirect_response(request.POST)
        else:
            raise SuspiciousOperation("Unexpected form action '%s' received" % request.POST.get("action"))
    else:
        util.initialize_form(id)

    return render_to_response('admin/cabinet/view_user_file.html', util.data, context_instance=RequestContext(request))
