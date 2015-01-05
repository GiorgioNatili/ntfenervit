# Create your views here.
from django.contrib import messages
from django.contrib.messages import get_messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import requires_csrf_token
from backend.utils import get_its_users
from contacts.models import Region, Province, Company, Payment, Visit, ChampionsDelivery, Contact, Division, SubDivision, Sector, Work, RankingConfiguration
from cabinet.models import Cabinet, UploadedFile, ContactFile
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.template import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import ModelForm, forms
from django import forms
from django.db.models import CharField
from django.db.models import  Q
from datetime import datetime
from django.core import serializers
import xlrd
import math
import json

from campaigns.models import NewsletterTarget, EventSignup, ITSRelConsultant, PointOfSaleType
from survey.models import Submission, Answer
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

from cabinet.models import ContactRefFile, ContactCertFile


class CompanyForm(ModelForm):
    class Meta:
        model = Company


class DivisionForm(ModelForm):
    class Meta:
        model = Division


class SectorForm(ModelForm):
    class Meta:
        model = Sector


class SubDivisionForm(ModelForm):
    class Meta:
        model = SubDivision


class WorkForm(ModelForm):
    class Meta:
        model = Work


class ContactForm(ModelForm):
    its = forms.TextInput()

    class Meta:
        model = Contact

class AllContactsForm(forms.Form):
    search = forms.CharField(label="Cerca", required=False)

class AllCompanyForm(forms.Form):
    search = forms.CharField(label="Cerca", required=False)

class ImportContactsForm(forms.Form):
    file = forms.FileField(label="Seleziona file EXCEL da importare")

class RankingConfigurationForm(ModelForm):
    class Meta:
        model = RankingConfiguration

#########################
####  COMPANY CRUD ######
#########################

@requires_csrf_token
@staff_member_required
def view_company(request):
    #companies = Company.objects.all().order_by('name', 'company_code', 'city', 'type')
    #return render_to_response('admin/contacts/view_company.html', {'companies': companies}, context_instance=RequestContext(request))
    limit = 10
    offset = 0
    #newsearch = False
    count = Company.objects.count()
    if request.method == 'POST':
        form = AllCompanyForm(request.POST)
        if form.is_valid():
            search = request.POST['search']
            limit = int(request.POST['limit'])
            pageoffset = int(request.POST['offset'])
            newsearch = request.POST.get('newsearch', False)
            if search != "":
                count = Company.objects.filter(Q(name__icontains=search) | Q(city__icontains=search) | Q(vat__icontains=search)).count()
            clicked_page = int(request.POST['clicked'])
            if not newsearch:
                offset = 0
            else:
                if clicked_page == -4:
                    #Primo
                    offset = 0
                elif clicked_page == -3:
                    #Precedente
                    offset = pageoffset - limit
                elif clicked_page == -2:
                    #Prossimo
                    offset = pageoffset + limit
                elif clicked_page == -1:
                    #Ultimo
                    offset = (int(math.ceil(count/float(limit))) - 1) * limit
                else:
                    offset = limit * (clicked_page-1)
            if search == "":
                companies = Company.objects.all().order_by('name', 'company_code', 'city', 'type')[offset:limit+offset]
            else:
                companies = Company.objects.filter(Q(name__icontains=search) | Q(city__icontains=search) | Q(vat__icontains=search)).order_by('name', 'company_code', 'city', 'type')[offset:limit+offset]
    else:
        form = AllCompanyForm()
        companies = Company.objects.all().order_by('name', 'company_code', 'city', 'type')[offset:limit]
    
    temp = count/ float(limit)
    pages = int(math.ceil(temp))
    t = (offset+1)/ float(limit)
    actual = int(math.ceil(t))
    if actual > pages:
        actual = pages
    if actual < 1:
        actual = 1
    
    init_page = 1
    end_page = pages + 1
    if actual > 3:
        init_page = actual - 2
    if actual < pages - 2:
        end_page = actual + 2 + 1
    
    return render_to_response('admin/contacts/view_company.html', {'companies': companies, 'form': form, 'count': count, 'limit': limit, 'offset': offset, 'pages': pages, 'actual': actual, 'range': range(init_page, end_page)}, context_instance=RequestContext(request))


@staff_member_required
def view_add_company(request):
    c = {}
    c.update(csrf(request))
    provinces = Province.objects.all()
    types = PointOfSaleType.objects.all()
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            new_company = form.save()
            if request.POST.has_key('_addanother'):
                form = CompanyForm()
            else:
                messages.success(request, 'Aggiunta azienda \"' + new_company.name + '\"')
                return HttpResponseRedirect('/admin/contacts/company')
        else:
            messages.error(request, 'Errore durante inserimento nuova azienda')
    c = {'form': form, 'provinces': provinces, 'types': types}
    return render_to_response('admin/contacts/view_add_company.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_company_details(request, id):
    company = get_object_or_404(Company, vat=id)
    provinces = Province.objects.all()
    types = PointOfSaleType.objects.all()
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            new_company = form.save(commit=False)
            new_company.save()
            messages.success(request, 'Azienda \"' + new_company.name + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/contacts/company')
        else:
            messages.error(request, 'Errore durante inserimento nuova azienda')
    return render_to_response('admin/contacts/view_company_details.html',
                              {'company': company, 'types': types, 'provinces': provinces, 'form': form},
                              context_instance=RequestContext(request))


##########################
####  DIVISION CRUD ######
#########################


@staff_member_required
def view_division(request):
    division = Division.objects.all()
    return render_to_response('admin/contacts/view_division.html', {'divisions': division},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_division(request):
    c = {}
    c.update(csrf(request))
    form = DivisionForm()
    if request.method == 'POST':
        form = DivisionForm(request.POST)
        if form.is_valid():
            new_division = form.save()
            if request.POST.has_key('_addanother'):
                form = DivisionForm()
            else:
                messages.success(request, 'Aggiunta divisione \"' + new_division.name + '\"')
                return HttpResponseRedirect('/admin/contacts/division')
    c = {'form': form}
    return render_to_response('admin/contacts/view_add_division.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_division_details(request, id):
    division = get_object_or_404(Division, id=id)
    form = DivisionForm()
    if request.method == 'POST':
        form = DivisionForm(request.POST, instance=division)
        if form.is_valid():
            new_division = form.save(commit=False)
            new_division.save()
            messages.success(request, 'Divisione \"' + new_division.name + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/contacts/division')
    return render_to_response('admin/contacts/view_division_details.html', {'division': division, 'form': form},
                              context_instance=RequestContext(request))


##########################
### SUBDIVISION CRUD ####
#########################

@staff_member_required
def view_subdivision(request):
    subdivision = SubDivision.objects.all()
    return render_to_response('admin/contacts/view_subdivision.html', {'subdivisions': subdivision},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_subdivision(request):
    c = {}
    c.update(csrf(request))
    form = SubDivisionForm()
    divisions = Division.objects.all()
    if request.method == 'POST':
        form = SubDivisionForm(request.POST)
        if form.is_valid():
            new_subdivision = form.save()
            if request.POST.has_key('_addanother'):
                form = SubDivisionForm()
            else:
                messages.success(request, 'Aggiunta sottocategoria \"' + new_subdivision.name + '\"')
                return HttpResponseRedirect('/admin/contacts/subdivision')
    c = {'form': form, 'divisions': divisions}
    return render_to_response('admin/contacts/view_add_subdivision.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_subdivision_details(request, id):
    subdivision = get_object_or_404(SubDivision, id=id)
    form = SubDivisionForm()
    divisions = Division.objects.all()
    if request.method == 'POST':
        form = SubDivisionForm(request.POST, instance=subdivision)
        if form.is_valid():
            new_subdivision = form.save(commit=False)
            new_subdivision.save()
            messages.success(request, 'Sottocategoria \"' + new_subdivision.name + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/contacts/subdivision')
    return render_to_response('admin/contacts/view_subdivision_details.html',
                              {'subdivision': subdivision, 'divisions': divisions, 'form': form},
                              context_instance=RequestContext(request))


def view_subdivision_rest(request):
    division = request.GET.get('division', '')
    from django.core import serializers

    json_subcat = serializers.serialize("json", SubDivision.objects.filter(category=division))
    return HttpResponse(json_subcat, mimetype="application/javascript")

##########################
##### SECTOR CRUD ########
#########################

@staff_member_required
def view_sector(request):
    sector = Sector.objects.all()
    return render_to_response('admin/contacts/view_sector.html', {'sectors': sector},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_sector(request):
    c = {}
    c.update(csrf(request))
    form = SectorForm()
    if request.method == 'POST':
        form = SectorForm(request.POST)
        if form.is_valid():
            new_sector = form.save()
            if request.POST.has_key('_addanother'):
                form = SectorForm()
            else:
                messages.success(request, 'Aggiunto Settore \"' + new_sector.name + '\"')
                return HttpResponseRedirect('/admin/contacts/sector')
    c = {'form': form}
    return render_to_response('admin/contacts/view_add_sector.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_sector_details(request, id):
    sector = get_object_or_404(Sector, id=id)
    form = SectorForm()
    if request.method == 'POST':
        form = SectorForm(request.POST, instance=sector)
        if form.is_valid():
            new_sector = form.save(commit=False)
            new_sector.save()
            messages.success(request, 'Settore \"' + new_sector.name + '\" aggiornato correttamente!')
            return HttpResponseRedirect('/admin/contacts/sector')
    return render_to_response('admin/contacts/view_sector_details.html', {'sector': sector, 'form': form},
                              context_instance=RequestContext(request))


##########################
##### WORK CRUD ########
#########################


@staff_member_required
def view_work(request):
    work = Work.objects.all()
    return render_to_response('admin/contacts/view_work.html', {'works': work},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_work(request):
    c = {}
    c.update(csrf(request))
    form = WorkForm()
    sectors = Sector.objects.all()
    if request.method == 'POST':
        form = WorkForm(request.POST)
        if form.is_valid():
            new_work = form.save()
            if request.POST.has_key('_addanother'):
                form = WorkForm()
            else:
                messages.success(request, 'Aggiunta professione \"' + new_work.name + '\"')
                return HttpResponseRedirect('/admin/contacts/work')
    c = {'form': form, 'sectors': sectors}
    return render_to_response('admin/contacts/view_add_work.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_work_details(request, id):
    work = get_object_or_404(Work, id=id)
    form = WorkForm()
    sectors = Sector.objects.all()
    if request.method == 'POST':
        form = WorkForm(request.POST, instance=work)
        if form.is_valid():
            new_work = form.save(commit=False)
            new_work.save()
            messages.success(request, 'Professione \"' + new_work.name + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/contacts/work')
    return render_to_response('admin/contacts/view_work_details.html', {'work': work, 'sectors': sectors, 'form': form},
                              context_instance=RequestContext(request))


def view_work_rest(request):
    sector = request.GET.get('sector', '')
    from django.core import serializers

    json_subcat = serializers.serialize("json", Work.objects.filter(sector=sector))
    return HttpResponse(json_subcat, mimetype="application/javascript")

##########################
####  CONTACT CRUD ######
#########################

@staff_member_required
def view_contact(request):
    limit = 10
    offset = 0
    #newsearch = False
    count = Contact.objects.count()
    #contacts = Contact.objects.all()[offset:limit]
    if request.method == 'POST':
        form = AllContactsForm(request.POST)
        if form.is_valid():
            search = request.POST['search']
            limit = int(request.POST['limit'])
            pageoffset = int(request.POST['offset'])
            newsearch = request.POST.get('newsearch', False)
            if search != "":
                count = Contact.objects.filter(Q(name__icontains=search) | Q(surname__icontains=search) | Q(code__icontains=search) | Q(email__icontains=search) | Q(street__icontains=search) | Q(civic__icontains=search) | Q(city__icontains=search)).count()
            clicked_page = int(request.POST['clicked'])
            if not newsearch:
                offset = 0
            else:
                if clicked_page == -4:
                    #Primo
                    offset = 0
                elif clicked_page == -3:
                    #Precedente
                    offset = pageoffset - limit
                elif clicked_page == -2:
                    #Prossimo
                    offset = pageoffset + limit
                elif clicked_page == -1:
                    #Ultimo
                    offset = (int(math.ceil(count/float(limit))) - 1) * limit
                else:
                    offset = limit * (clicked_page-1)
            if search == "":
                contacts = Contact.objects.all()[offset:limit+offset]
            else:
                contacts = Contact.objects.filter(Q(name__icontains=search) | Q(surname__icontains=search) | Q(code__icontains=search) | Q(email__icontains=search) | Q(street__icontains=search) | Q(civic__icontains=search) | Q(city__icontains=search))[offset:limit+offset]
    else:
        form = AllContactsForm()
        contacts = Contact.objects.all()[offset:limit]
    
    temp = count/ float(limit)
    pages = int(math.ceil(temp))
    t = (offset+1)/ float(limit)
    actual = int(math.ceil(t))
    if actual > pages:
        actual = pages
    if actual < 1:
        actual = 1
    
    init_page = 1
    end_page = pages + 1
    if actual > 3:
        init_page = actual - 2
    if actual < pages - 2:
        end_page = actual + 2 + 1
    
    return render_to_response('admin/contacts/view_contact.html', {'contacts': contacts, 'form': form, 'count': count, 'limit': limit, 'offset': offset, 'pages': pages, 'actual': actual, 'range': range(init_page, end_page)},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_contact(request):
    c = {}
    c.update(csrf(request))
    provinces = Province.objects.all()
    companies = Company.objects.all()
    sectors = Sector.objects.all()
    divisions = Division.objects.all()
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            new_contact = form.save()
            messages.success(request, 'Aggiunta contatto \"' + new_contact.name + ' ' + new_contact.surname + '\"')
            if '_addanother' in request.POST:
                form = ContactForm()
            else:
                return HttpResponseRedirect('/admin/contacts/contact')
        else:
            messages.error(request, 'Errore in inserimento contatto')
    c = {'form': form, 'provinces': provinces, 'companies': companies, 'sectors': sectors, 'divisions': divisions}
    return render_to_response('admin/contacts/view_add_contact.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_contact_details(request, id):
    contact = get_object_or_404(Contact, code=id)
    owner = contact.owner_id

    # Lookup the ITS Relationship table.  If not found, return None
    try:
        itsrel = ITSRelConsultant.objects.get(consultant=contact)
    except ITSRelConsultant.DoesNotExist:
        itsrel = None
    # Find ITS user


    # Prepare data for dropdowns
    its_users = get_its_users()

    refiles = ContactRefFile.objects.filter(contact=contact)
    certfiles = ContactCertFile.objects.filter(contact=contact)

    provinces = Province.objects.all()

    #companies = Company.objects.all()[:100]
    sectors = Sector.objects.all()
    divisions = Division.objects.all()

    sector = None
    works = None
    if contact.work and contact.work.sector:
        sector = Sector.objects.filter(id=contact.work.sector.id)
    if sector is not None:
        works = Work.objects.all().filter(sector=sector)

    ana_division = None
    subdivisions = None
    if contact.anagrafic_subdivision.all():
        ana_division = Division.objects.filter(id=contact.anagrafic_subdivision.all()[0].category.id)
        subdivisions = SubDivision.objects.all().filter(category=ana_division)

    submissions = Submission.objects.all().filter(contact=contact)
    submissions2 = []
    for sb in submissions:
        answers = Answer.objects.all().filter(submission=sb)
        sb.total_score = 0
        sb.score = 0
        for ans in answers:
            sb.total_score += ans.question.score
            if ans.value.lower() == ans.question.correct_answer.lower():
                sb.score += ans.question.score
        submissions2.append(sb)

    event_signup = EventSignup.objects.all().filter(contact=contact)
    newsletter_target = NewsletterTarget.objects.all().filter(contact=contact)

    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            new_contact = form.save(commit=False)

            # Update ITS Relationship table
            if new_contact.type == "C":
                # Check if ITS dropdown was selected with a valid ITS
                its_id = request.POST.get("its")
                if its_id != "---":
                    # If ITS Relationship exists, updated it.  Create one otherwise
                    if itsrel:
                        itsrel.its = User.objects.get(pk=its_id)
                    else:
                        itsrel = ITSRelConsultant(consultant=contact, its_id=its_id)

                    itsrel.save()
            else:
                # If resetting from Consultant to Normal, clear the ITS Relationship
                if itsrel:
                    itsrel.delete()

            if owner:
                new_contact.owner = User.objects.all().filter(id=owner)[0]
                if new_contact.status == 'C':
                   userLoc = User.objects.all().filter(id=owner)[0]
                   userLoc.is_active = False
                   userLoc.save()
                else:
                   userLoc = User.objects.all().filter(id=owner)[0]
                   userLoc.is_active = True
                   userLoc.save()
            new_contact.save()
            messages.success(request,
                             'Contatto \"' + new_contact.name + ' ' + new_contact.surname + '\" aggiornato correttamente!')
            return HttpResponseRedirect('/admin/contacts/contact/'+id)

    return render_to_response(
        'admin/contacts/view_contact_details.html',
        {
            'submissions': submissions2,
            'event_signup': event_signup,
            'newsletter_target':newsletter_target,
            'contact': contact,
            'itsrel': itsrel,
            'provinces': provinces,
            #'companies': companies,
            'sectors': sectors,
            'sector':sector,
            'works':works,
            'divisions': divisions,
            'ana_division':ana_division,
            'subdivisions':subdivisions,
            'refiles': refiles,
            'certfiles': certfiles,
            'its_users': its_users,
            'form': form
        },
        context_instance=RequestContext(request))

def search_companies(request):
    if request.method == 'POST':
        search = request.POST.get('text')
        limit = int(request.POST.get('limit'))
        pageoffset = int(request.POST.get('offset', 0))
        clicked_page = int(request.POST.get('clicked'))
        newsearch = request.POST.get('newsearch', False)
        
        count = Company.objects.count()
        if search != "":
            count = Company.objects.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(street__icontains=search) | Q(city__icontains=search) | Q(vat__icontains=search)).count()
        if not newsearch:
            offset = 0
        else:
            if clicked_page == -4:
                #Primo
                offset = 0
            elif clicked_page == -3:
                #Precedente
                offset = pageoffset - limit
            elif clicked_page == -2:
                #Prossimo
                offset = pageoffset + limit
            elif clicked_page == -1:
                #Ultimo
                offset = (int(math.ceil(count/float(limit))) - 1) * limit
            else:
                offset = limit * (clicked_page-1)
        if search == "":
            companies = Company.objects.all().order_by('name', 'company_code', 'city', 'type')[offset:limit+offset]
        else:
            companies = Company.objects.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(street__icontains=search) | Q(city__icontains=search) | Q(vat__icontains=search)).order_by('name', 'company_code', 'city', 'type')[offset:limit+offset]
        
        temp = count/ float(limit)
        pages = int(math.ceil(temp))
        t = (offset+1)/ float(limit)
        actual = int(math.ceil(t))
        if actual > pages:
            actual = pages
        if actual < 1:
            actual = 1
    
        init_page = 1
        end_page = pages + 1
        if actual > 3:
            init_page = actual - 2
        if actual < pages - 2:
            end_page = actual + 2 + 1
        
        response_data = {}
        response_data['companies'] = serializers.serialize("json", companies)
        response_data['count'] = count
        response_data['limit'] = limit
        response_data['offset'] = offset
        response_data['pages'] = pages
        response_data['actual'] = actual
        response_data['range'] = range(init_page, end_page)
        
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"error": "Errore generico."}),
            content_type="application/json"
        )

@staff_member_required
def view_contact_import(request):
    form = ImportContactsForm()
    message = ''
    errorList = []
    if request.method == 'POST':
        form = ImportContactsForm(request.POST,request.FILES)
        my_file = request.FILES['file']
        if form.is_valid():
            with open('/var/www/yellowpage/media/xls/'+my_file.name, 'wb+') as destination:
                for chunk in my_file.chunks():
                    destination.write(chunk)
            xls = xlrd.open_workbook('/var/www/yellowpage/media/xls/'+my_file.name)
            sheet = xls.sheet_by_index(0)
            completed = 0
            for row_index in range(1, sheet.nrows):
                try:
                    contact = Contact(code=sheet.cell_value(row_index,0).capitalize())
                    contact.surname = sheet.cell_value(row_index,1).capitalize()
                    contact.name = sheet.cell_value(row_index,2).capitalize()
                    contact.street = sheet.cell_value(row_index,3).capitalize()
                    contact.zip = str(sheet.cell_value(row_index,4))
                    contact.city = sheet.cell_value(row_index,5).capitalize()
                    contact.province = Province.objects.get(code=sheet.cell_value(row_index,6))
                    contact.email = sheet.cell_value(row_index,7)
                    contact.phone_number = sheet.cell_value(row_index, 11)
                    contact.birthdate = str(sheet.cell_value(row_index,10))
                    #Settore
                    sectorString = str(sheet.cell_value(row_index, 9))
                    professionString = str(sheet.cell_value(row_index, 8))
                    profession = Work.objects.filter(name=professionString)
                    if not profession:
                        sector = Sector.objects.filter(name=sectorString)
                        if not sector:
                            sector = Sector(name=sectorString)
                            sector.save()
                        #Professione
                        profession = Work(name=professionString, sector=Sector.objects.get(pk=sector.pk))
                        profession.save()
                    else:
                        profession = profession[0]
                    contact.work = Work.objects.get(name=profession.name)
                    contact.save()
                    completed += 1
                    #Certificato
                    cabinet = Cabinet.objects.get(pk=2)
                    current_user = request.user
                    file = ContactFile(contact=Contact.objects.get(pk=contact.pk))
                    uploadedFile = UploadedFile(title="Certificato Vuoto", cabinet=cabinet, file_ref="/cabinet/cert_empty.pdf", owner=current_user)
                    file.file = uploadedFile
                except Exception as e:
                    print '%s (%s)' % (e.message, type(e))
                    errorList.append(sheet.cell_value(row_index,0).capitalize())
            message = 'Report Import: %d contatti importati correttamente. ' % completed

    return render_to_response('admin/contacts/view_contact_import.html',{'form':form, 'message':message, 'errorList': errorList}, context_instance=RequestContext(request))


@user_passes_test(lambda u:u.is_superuser)
def view_ranking_details(request,id):
    ranking = get_object_or_404(RankingConfiguration, id=id)
    form = RankingConfigurationForm()
    if request.method == 'POST':
        form = RankingConfigurationForm(request.POST, instance=ranking)
        if form.is_valid():
            new_ranking = form.save(commit=False)
            new_ranking.save()
            messages.success(request, 'Ranking aggiornato correttamente!')
            return HttpResponseRedirect('/admin/contacts/ranking/details/'+id)
    return render_to_response('admin/contacts/view_ranking_details.html',
                              {'ranking': ranking,'form': form},
                              context_instance=RequestContext(request))

from forms import ContactSearchForm
from haystack.query import SearchQuerySet
import xlwt
@staff_member_required
def search_contact(request):
    provinces = Province.objects.all()
    companies = Company.objects.all()
    works = Work.objects.all()

    form = ContactSearchForm(request.GET)
    search_query = request.GET.get("q", None)
    contacts = None
    ranking_args = {}

    if 'q' in request.GET:
        results = form.search()

        comp_rank_from = request.GET.get("comp_rank_from", None)
        comp_rank_to = request.GET.get("comp_rank_to", None)
        part_rank_from = request.GET.get("part_rank_from", None)
        part_rank_to = request.GET.get("part_rank_to", None)

        ranking_args = {
            "comp_rank_from": comp_rank_from,
            "comp_rank_to": comp_rank_to,
            "part_rank_from": part_rank_from,
            "part_rank_to": part_rank_to
        }

        if comp_rank_from and comp_rank_to:
            # print "### comp range: %s, %s" % (comp_rank_from, comp_rank_to)
            results = results.filter(company_ranking__range=[comp_rank_from, comp_rank_to])
        elif comp_rank_from:
            # print "### comp from: %s" % comp_rank_from
            results = results.filter(company_ranking__gte=comp_rank_from)
        elif comp_rank_to:
            # print "### comp to: %s" % comp_rank_to
            results = results.filter(company_ranking__lte=comp_rank_to)


        if part_rank_from and part_rank_to:
            # print "### part range: %s, %s" % (part_rank_from, part_rank_to)
            results = results.filter(participation_ranking__range=[part_rank_from, part_rank_to])
        elif part_rank_from:
            # print "### part from: %s" % part_rank_from
            results = results.filter(participation_ranking__gte=part_rank_from)
        elif part_rank_to:
            # print "### part to: %s" % part_rank_to
            results = results.filter(participation_ranking__lte=part_rank_to)


        if len(results) > 0:
            # contacts = Contact.objects.filter(pk__in=[r.pk for r in results])
            contacts = []
            max_results = int(request.GET.get('max_results', 10000))
            for r in results:
                # print "### r: %s" % r
                if r is not None and r.model_name == 'contact':
                    contacts.append(r.object)
                    if len(contacts) >= max_results:
                        break

    return render_to_response('admin/search/search_contact.html', {
        'search_query' : search_query,
        'ranking_args': ranking_args,
        'contacts': contacts,
        'form' : form,
        'provinces' : provinces,
        'companies' : companies,
        'works' : works,
    }, context_instance=RequestContext(request))

@staff_member_required
def search_contact_export(request):
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=esportazione_ricerca_contatti.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Foglio 1')
    ws.write(0, 0, 'Identificativo')
    ws.write(0,1,'Username')
    ws.write(0, 2, 'Cognome')
    ws.write(0, 3, 'Nome')
    ws.write(0, 4, 'Sesso')
    ws.write(0, 5, 'Data Di nascita')
    ws.write(0, 6, 'Indirizzo')
    ws.write(0, 7, 'CAP')
    ws.write(0, 8, 'Citta\'')
    ws.write(0, 9, 'Prov')
    ws.write(0, 10, 'Regione')
    ws.write(0, 11, 'Email')
    ws.write(0, 12, 'Qualifica')
    ws.write(0, 13, 'Categoria')
    ws.write(0,14,'Ranking Aziendale')
    ws.write(0,15,'Ranking Partecipazione')
    ws.write(0,16,'Status')

    form = ContactSearchForm(request.GET)
    results = []
    if request.GET.has_key('q'):
        results = form.search()
        # if request.GET.has_key('max_results'):
        #     results = form.search()[:request.GET.get('max_results')]
        # else:
        #     results = form.search()
    contacts = []
    if len(results) > 0:
        max_results = int(request.GET.get('max_results', 10000))
        for r in results:
            if r is not None and r.model_name == 'contact':
                contacts.append(r.object)
                if len(contacts) >= max_results:
                    break
        row = 1
        for c in contacts:
            ws.write(row,0,c.code)
            if c.owner != None:
                ws.write(row,1,c.owner.username)

            ws.write(row,2,c.surname)
            ws.write(row,3,c.name)
            ws.write(row,4,c.sex)
            if c.birthdate:
                ws.write(row,5,c.birthdate.strftime("%d/%m/%Y"))

            ws.write(row,6,c.street+" "+c.civic)
            ws.write(row,7,c.zip)
            ws.write(row,8,c.city)

            if c.province:
                ws.write(row,9,c.province.code)
                ws.write(row,10,c.province.region.name)

            ws.write(row,11,c.email)
            if c.work:
                ws.write(row,12,c.work.name.capitalize())
                ws.write(row,13,c.work.sector.name.capitalize())

            ws.write(row,14,c.company_ranking)
            ws.write(row,15,c.participation_ranking)
            if c.status == 'A':
                ws.write(row,16,"Attivo")
            if c.status == 'N':
                ws.write(row,16,"Non Attivo")
            if c.status == 'I':
                ws.write(row,16,"Inerte")
            if c.status == 'C':
                ws.write(row,16,"Cancellato")
            if c.status == 'D':
                ws.write(row,16,"Non Interessato")
            row +=1
    wb.save(response)
    return response
