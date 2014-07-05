
import datetime
from django.forms import ModelForm
from django.template import RequestContext
from cabinet.models import Cabinet, UploadedFile, UserRefFile, UserCertFile
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import user_passes_test

class UploadedFileForm(ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('title', 'cabinet', 'file_ref', 'owner')

class UserRefFileForm(ModelForm):
    class Meta:
        model = UserRefFile
        fields = ('user','file','event')

class UserCertFileForm(ModelForm):
    class Meta:
        model = UserCertFile

def __view_user_file_common(**kwargs):
    '''
    Set up the view_user_file.html form status based on `file_type` and `action`
    '''

    # Setting based on Cabinate type: references or certificates
    if kwargs["file_type"] == "ref":
        kwargs["page_title"] = "Files"
        kwargs["cabinet_id"] = UserRefFile.CABINET_REFERENCE
        user_file_object = UserRefFile
        object_name = "file"
    else:
        kwargs["page_title"] = "Certificati"
        kwargs["cabinet_id"] = UserCertFile.CABINET_CERTIFICATE
        user_file_object = UserCertFile
        object_name = "certificato"

    # Setting based on action
    if kwargs["action"] == "add":
        kwargs["icon_name"] = "icon-plus"
        kwargs["page_subtitle"] = "Aggiungi un nuovo %s" % object_name
        kwargs["form"] = user_file_object()
        kwargs["upload_form"] = UploadedFileForm()
    else:
        kwargs["icon_name"] = "icon-file"
        kwargs["page_subtitle"] = "Visualizza e modifica gli attributi dell'%s selezionato" % object_name

    return kwargs

@user_passes_test(lambda u:u.is_superuser)
def view_user_file_add(request, user_id, type):
    params = __view_user_file_common(
        action="add",
        file_type=type,
        user_id=user_id,
        owner_id=request.user.id
    )

    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES)

        if form.is_valid():
            # ToDo: Need to add db transaction
            file = form.save()

            if type == "ref":
                userFile = UserRefFile(user_id=user_id, file=file)
            else:
                dt = request.POST.get("expiry")
                userFile = UserCertFile(user_id=user_id, file=file, expiry=datetime.datetime.strptime(dt, "%d/%m/%Y"))

            userFile.save()
            # ToDo: check if referer exists
            return HttpResponseRedirect(request.POST.get("referer"))

        else:
            print "form is_valid: %s" % form.errors
            params["upload_form"] = form;

    else:
        params["referer"] = request.META.get('HTTP_REFERER')
        print "referer: %s" % request.META.get('HTTP_REFERER')

        #file = UploadedFile(title=data.get("title"), cabinet_id=data.get("cabinet_id"), file_ref = request.FILES['file_ref'], owner=request.user)
        #file.save()


    return render_to_response('admin/cabinet/view_user_file.html', params,context_instance=RequestContext(request))


@user_passes_test(lambda u:u.is_superuser)
def view_user_file(request, user_id, type, id):
    params = __view_user_file_common(action="view", user_id=user_id, file_type=type, file_id=id)
    return render_to_response('admin/cabinet/view_user_file.html', params)