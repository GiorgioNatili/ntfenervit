# Create your views here.

import datetime
from django.contrib import messages
from django.contrib.messages import get_messages
from django.shortcuts import render_to_response, get_object_or_404
from django.template import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import ModelForm,forms
from django.contrib.auth.models import User,Group,Permission
from django.contrib.auth.decorators import user_passes_test
from django.forms import ModelForm,forms

from contacts.models import Contact
from cabinet.models import Cabinet, UploadedFile, UserRefFile, UserCertFile

class UserForm(ModelForm):
    class Meta:
        model = User

class GroupForm(ModelForm):
    class Meta:
        model = Group

@staff_member_required
def user_list(request):
   users = User.objects.all()
   contacts = []
   for u in users:
       if not u.is_staff:
           contact = Contact.objects.all().filter(owner=u)
           if len(contact)>0:
               contacts.append(contact[0])
   print contacts
   return render_to_response('admin/backend/users_list.html', {"users":users,"contacts":contacts},
                             context_instance=RequestContext(request))

@user_passes_test(lambda u:u.is_superuser)
def user_details(request,id):
    user = get_object_or_404(User,id=id)
    refiles = UserRefFile.objects.filter(user_id=id)
    certfiles = UserCertFile.objects.filter(user_id=id)
    contact = None
    gruppo = None
    print user.groups.all()
    if len(user.groups.all())>0:
        gruppo = user.groups.all()[0]
    gruppi = Group.objects.all()
    print gruppo
    if not user.is_staff:
        contact = Contact.objects.all().filter(owner=user)[0]
    form = UserForm()
    if request.method == 'POST':
        print request.POST
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.save()
            if request.POST.get("gruppo") != '-1':
                new_user.groups.clear()
                gruppo = Group.objects.all().filter(id=request.POST.get("gruppo"))[0]
                new_user.groups.add(gruppo)
            messages.success(request, 'Utente \"' + new_user.username + '\" aggiornato correttamente!')
            return HttpResponseRedirect('/admin/backend/utenti')
    return render_to_response('admin/backend/view_user_details.html',
                              {'usr': user, 'form': form,'contact':contact,'ugruppo':gruppo,"gruppi":gruppi, "refiles": refiles, "certfiles": certfiles},
                              context_instance=RequestContext(request))

@user_passes_test(lambda u:u.is_superuser)
def user_add(request):
    c = {}
    c.update(csrf(request))
    form = UserForm()
    gruppi = Group.objects.all()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.set_password(request.POST.get("password"))
            new_user.save()
            if request.POST.get("gruppo") != '-1':
                gruppo = Group.objects.all().filter(id=request.POST.get("gruppo"))[0]
                new_user.groups.add(gruppo)
            if request.POST.has_key('_addanother'):
                form = UserForm()
            else:
                messages.success(request, 'Aggiunto utente \"' + new_user.username + '\"')
                return HttpResponseRedirect('/admin/backend/utenti')
    c = {'form': form,'gruppi':gruppi}
    return render_to_response('admin/backend/view_add_user.html', c, context_instance=RequestContext(request))


@user_passes_test(lambda u:u.is_superuser)
def group_list(request):
    groups = Group.objects.all()
    return render_to_response('admin/backend/groups_list.html', {"groups":groups},
                              context_instance=RequestContext(request))

@user_passes_test(lambda u:u.is_superuser)
def group_add(request):
    c = {}
    c.update(csrf(request))
    form = GroupForm()
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save()
            if request.POST.get("add_contact") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_contact"))
            if request.POST.get("change_contact") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_contact"))
            if request.POST.get("delete_contact") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_contact"))
            if request.POST.get("add_campaign") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_campaign"))
            if request.POST.get("change_contact") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_contact"))
            if request.POST.get("delete_campaign") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_campaign"))
            if request.POST.get("add_event") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_event"))
            if request.POST.get("add_event") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_event"))
            if request.POST.get("change_event") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_event"))
            if request.POST.get("delete_event") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_event"))
            if request.POST.get("change_eventsignup") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_eventsignup"))
            if request.POST.get("add_newsletter") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_newsletter"))
            if request.POST.get("change_newsletter") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_newsletter"))
            if request.POST.get("delete_newsletter") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_newsletter"))
            if request.POST.get("add_newsletterschedulation") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_newsletterschedulation"))
            if request.POST.get("add_newslettertemplate") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_newslettertemplate"))
            if request.POST.get("change_newslettertemplate") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_newslettertemplate"))
            if request.POST.get("delete_newslettertemplate") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_newslettertemplate"))
            if request.POST.get("add_survey") == "on":

                new_group.permissions.add(Permission.objects.all().filter(codename="add_survey")[0])
            if request.POST.get("change_survey") == "on":
                new_group.permissions.add(Permission.objects.all().filter(codename="change_survey")[0])
            if request.POST.get("delete_survey") == "on":
                new_group.permissions.add(Permission.objects.all().filter(codename="delete_survey")[0])
            new_group.save()
            if request.POST.has_key('_addanother'):
                form = GroupForm()
            else:
                messages.success(request, 'Aggiunto gruppo \"' + new_group.name + '\"')
                return HttpResponseRedirect('/admin/backend/gruppi')
    c = {'form': form}
    return render_to_response('admin/backend/view_add_group.html', c, context_instance=RequestContext(request))

@user_passes_test(lambda u:u.is_superuser)
def group_details(request,id):
    group = get_object_or_404(Group,id=id)
    permissions = group.permissions.all()
    permissions_s = []
    for p in permissions:
        permissions_s.append(p.codename)
    form = GroupForm()
    if request.method == 'POST':
        print request.POST
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            new_group = form.save(commit=False)
            if request.POST.get("add_contact") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_contact"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="add_contact"))
            if request.POST.get("change_contact") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_contact"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="change_contact"))
            if request.POST.get("delete_contact") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_contact"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="delete_contact"))
            if request.POST.get("add_campaign") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_campaign"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="add_campaign"))
            if request.POST.get("change_contact") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_contact"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="change_contact"))
            if request.POST.get("delete_campaign") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_campaign"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="delete_campaign"))
            if request.POST.get("add_event") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_event"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="add_event"))
            if request.POST.get("add_event") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_event"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="add_event"))
            if request.POST.get("change_event") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_event"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="change_event"))
            if request.POST.get("delete_event") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_event"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="delete_event"))
            if request.POST.get("change_eventsignup") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_eventsignup"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="change_eventsignup"))
            if request.POST.get("add_newsletter") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_newsletter"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="add_newsletter"))
            if request.POST.get("change_newsletter") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_newsletter"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="change_newsletter"))
            if request.POST.get("delete_newsletter") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_newsletter"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="delete_newsletter"))
            if request.POST.get("add_newsletterschedulation") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_newsletterschedulation"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="add_newsletterschedulation"))
            if request.POST.get("add_newslettertemplate") == "on":
                new_group.permissions.add(Permission.objects.get(codename="add_newslettertemplate"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="add_newslettertemplate"))
            if request.POST.get("change_newslettertemplate") == "on":
                new_group.permissions.add(Permission.objects.get(codename="change_newslettertemplate"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="change_newslettertemplate"))
            if request.POST.get("delete_newslettertemplate") == "on":
                new_group.permissions.add(Permission.objects.get(codename="delete_newslettertemplate"))
            else:
                new_group.permissions.remove(Permission.objects.get(codename="delete_newslettertemplate"))
            if request.POST.get("add_survey") == "on":
                new_group.permissions.add(Permission.objects.filter(codename="add_survey")[0])
            else:
                new_group.permissions.remove(Permission.objects.filter(codename="add_survey")[0])
            if request.POST.get("change_survey") == "on":
                new_group.permissions.add(Permission.objects.filter(codename="change_survey")[0])
            else:
                new_group.permissions.remove(Permission.objects.filter(codename="change_survey")[0])
            if request.POST.get("delete_survey") == "on":
                new_group.permissions.add(Permission.objects.filter(codename="delete_survey")[0])
            else:
                new_group.permissions.remove(Permission.objects.filter(codename="delete_survey")[0])
            new_group.save()
            messages.success(request, 'Gruppo \"' + new_group.name + '\" aggiornato correttamente!')
            return HttpResponseRedirect('/admin/backend/gruppi')
    return render_to_response('admin/backend/view_group_details.html',
                              {'group': group, 'permissions':permissions_s,'form': form},
                              context_instance=RequestContext(request))

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


'''
UploadFile Section
'''
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
    params = __view_user_file_common(action="add", file_type=type, user_id=user_id, owner_id=request.user.id)

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

        else:
            print "form is_valid: %s" % form.errors
            params["upload_form"] = form;

        #file = UploadedFile(title=data.get("title"), cabinet_id=data.get("cabinet_id"), file_ref = request.FILES['file_ref'], owner=request.user)
        #file.save()


    return render_to_response('admin/backend/view_user_file.html', params,context_instance=RequestContext(request))


@user_passes_test(lambda u:u.is_superuser)
def view_user_file(request, user_id, type, id):
    params = __view_user_file_common(action="view", user_id=user_id, file_type=type, file_id=id)
    return render_to_response('admin/backend/view_user_file.html', params)