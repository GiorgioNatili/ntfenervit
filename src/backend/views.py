# Create your views here.

from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.template import *
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User,Group,Permission
from django.contrib.auth.decorators import user_passes_test
from django.forms import ModelForm
from campaigns.models import District, ITSRelDistrict
from contacts.models import Contact


ITS_GROUP_ID = 4

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
   return render_to_response('admin/backend/users_list.html', {"users":users,"contacts":contacts},
                             context_instance=RequestContext(request))

@user_passes_test(lambda u:u.is_superuser)
def user_details(request, id):
    user = get_object_or_404(User, id=id)
    contact = None
    gruppo = None

    # Get the list of district and if current user is part of a district
    districts = District.objects.all()
    try:
        district = ITSRelDistrict.objects.get(its_id=id)
    except ITSRelDistrict.DoesNotExist:
        district = None

    if len(user.groups.all())>0:
        gruppo = user.groups.all()[0]
    gruppi = Group.objects.all()

    if not user.is_staff:
        contact = Contact.objects.all().filter(owner=user)[0]
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        valid_form = form.is_valid()

        # Custom validation for ITS district
        post_gruppo = request.POST.get("gruppo")
        post_district = request.POST.get("district")
        if post_gruppo == str(ITS_GROUP_ID) and post_district == '-1':
            form._errors["distretto"] = form.error_class(["Campo obrigattorio"])
            valid_form = False

        if valid_form:
            new_user = form.save(commit=False)
            new_user.save()

            # print "### user form is valid.  Group: %s" % new_user.groups.all()[0].id
            if request.POST.get("gruppo") != '-1':
                new_user.groups.clear()
                gruppo = Group.objects.all().filter(id=request.POST.get("gruppo"))[0]
                new_user.groups.add(gruppo)
            messages.success(request, 'Utente \"' + new_user.username + '\" aggiornato correttamente!')

            # Saving district.  Check if user belong to ITS group
            if len(new_user.groups.all())>0 and new_user.groups.all()[0].id == ITS_GROUP_ID:
                post_district = request.POST.get("district")
                #print "### District %s to be saved" % post_district

                if district:
                    district.district_id = post_district
                else:
                    district = ITSRelDistrict(its=new_user, district_id=post_district)

                district.save()
            else:
                print "### Clearing district"
                if district:
                    district.delete()

            return HttpResponseRedirect('/admin/backend/utenti')

    return render_to_response('admin/backend/view_user_details.html',
                              {'usr': user, 'form': form,'contact':contact,'ugruppo':gruppo,"gruppi":gruppi,"districts": districts, "district": district, "its_group_id": ITS_GROUP_ID},
                              context_instance=RequestContext(request))

@user_passes_test(lambda u:u.is_superuser)
def user_add(request):
    c = {}
    c.update(csrf(request))
    form = UserForm()
    gruppi = Group.objects.all()

    if request.method == 'POST':
        form = UserForm(request.POST)
        valid_form = form.is_valid()

        # Custom validation for ITS district
        post_gruppo = request.POST.get("gruppo")
        post_district = request.POST.get("district")
        if post_gruppo == str(ITS_GROUP_ID) and post_district == '-1':
            form._errors["distretto"] = form.error_class(["Campo obrigattorio"])
            valid_form = False

        if valid_form:
            new_user = form.save()
            new_user.set_password(request.POST.get("password"))
            new_user.save()
            if request.POST.get("gruppo") != '-1':
                gruppo = Group.objects.all().filter(id=request.POST.get("gruppo"))[0]
                new_user.groups.add(gruppo)

            # Saving district.  Check if user belong to ITS group
            if len(new_user.groups.all())>0 and new_user.groups.all()[0].id == ITS_GROUP_ID:
                post_district = request.POST.get("district")
                district = ITSRelDistrict(its=new_user, district_id=post_district)
                district.save()

            if request.POST.has_key('_addanother'):
                form = UserForm()
            else:
                messages.success(request, 'Aggiunto utente \"' + new_user.username + '\"')
                return HttpResponseRedirect('/admin/backend/utenti')

    c = {
        'form': form,
        'gruppi':gruppi,
        'districts': District.objects.all(),
        'its_group_id': ITS_GROUP_ID
    }
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

