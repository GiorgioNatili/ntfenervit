# Create your views here.
from django.contrib import messages
from django.contrib.messages import get_messages
from contacts.models import Region, Province, Company, Payment, Visit, ChampionsDelivery, Contact, Division, SubDivision, Sector, Work, RankingConfiguration
from django.shortcuts import render_to_response, get_object_or_404
from django.template import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import ModelForm,forms
from xlrd import open_workbook,cellname

from campaigns.models import NewsletterTarget, EventSignup
from survey.models import Submission, Answer
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

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
    class Meta:
        model = Contact


class ImportContactsForm(forms.Form):
    file = forms.FileField(label="Seleziona file EXCEL da importare")

class RankingConfigurationForm(ModelForm):
    class Meta:
        model = RankingConfiguration

##########################
####  COMPANY CRUD ######
#########################

@staff_member_required
def view_company(request):
    companies = Company.objects.all()
    print get_messages(request)
    return render_to_response('admin/contacts/view_company.html', {'companies': companies},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_company(request):
    c = {}
    c.update(csrf(request))
    provinces = Province.objects.all()
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
    c = {'form': form, 'provinces': provinces}
    return render_to_response('admin/contacts/view_add_company.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_company_details(request, id):
    company = get_object_or_404(Company, vat=id)
    provinces = Province.objects.all()
    form = CompanyForm()
    if request.method == 'POST':
        print request.POST
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            new_company = form.save(commit=False)
            new_company.save()
            messages.success(request, 'Azienda \"' + new_company.name + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/contacts/company')
    return render_to_response('admin/contacts/view_company_details.html',
                              {'company': company, 'provinces': provinces, 'form': form},
                              context_instance=RequestContext(request))


##########################
####  DIVISION CRUD ######
#########################


@staff_member_required
def view_division(request):
    division = Division.objects.all()
    print get_messages(request)
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
        print request.POST
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
    print get_messages(request)
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
        print request.POST
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
    print get_messages(request)
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
        print request.POST
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
    print get_messages(request)
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
        print request.POST
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
    contacts = Contact.objects.all()
    print get_messages(request)
    return render_to_response('admin/contacts/view_contact.html', {'contacts': contacts},
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
            if request.POST.has_key('_addanother'):
                form = ContactForm()
            else:
                messages.success(request, 'Aggiunta contatto \"' + new_contact.name + ' ' + new_contact.surname + '\"')
                return HttpResponseRedirect('/admin/contacts/contact')
    c = {'form': form, 'provinces': provinces, 'companies': companies, 'sectors': sectors, 'divisions': divisions}
    return render_to_response('admin/contacts/view_add_contact.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_contact_details(request, id):
    contact = get_object_or_404(Contact, code=id)
    owner = contact.owner_id
    print owner

    provinces = Province.objects.all()

    companies = Company.objects.all()
    sectors = Sector.objects.all()
    divisions = Division.objects.all()

    sector = None
    works = None
    if contact.work and contact.work.sector:
       sector = Sector.objects.filter(id=contact.work.sector.id)
    if sector!=None:
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
            if owner:
                new_contact.owner = User.objects.all().filter(id=owner)[0]
                print new_contact.status
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
    return render_to_response('admin/contacts/view_contact_details.html',
                              {'submissions': submissions2, 'event_signup': event_signup,'newsletter_target':newsletter_target, 'contact': contact, 'provinces': provinces,  'companies': companies, 'sectors': sectors,'sector':sector, 'works':works,'divisions': divisions,'ana_division':ana_division,'subdivisions':subdivisions,'form': form},
                              context_instance=RequestContext(request))


@staff_member_required
def view_contact_import(request):
    form = ImportContactsForm()
    if request.method == 'POST':
        form = ImportContactsForm(request.POST,request.FILES)
        my_file = request.FILES['file']
        if form.is_valid():
            with open('/var/www/yellowpage/media/xls/'+my_file.name, 'wb+') as destination:
                for chunk in my_file.chunks():
                    destination.write(chunk)
            xls = open_workbook('/var/www/yellowpage/media/xls/'+my_file.name)
            sheet = xls.sheet_by_index(0)
            print sheet.name
            print sheet.nrows
            print sheet.ncols
            for row_index in range(sheet.nrows):
                if row_index > 0:
                    #for col_index in range(sheet.ncols):
                     #print cellname(row_index,col_index),'-',
                     #print sheet.cell(row_index,col_index).value
                    if sheet.cell(row_index,0).value != "" and  sheet.cell(row_index,1).value != "" and sheet.cell(row_index,20).value:
                        print "COGNOME: "+sheet.cell(row_index,0).value.capitalize()
                        print "NOME: "+sheet.cell(row_index,1).value.capitalize()
                        print "EMAIL: "+sheet.cell(row_index,7).value.lower()
                        print "CF: "+sheet.cell(row_index,20).value

            print "VALIDO!!!"
    return render_to_response('admin/contacts/view_contact_import.html',{'form':form}, context_instance=RequestContext(request))


@user_passes_test(lambda u:u.is_superuser)
def view_ranking_details(request,id):
    ranking = get_object_or_404(RankingConfiguration, id=id)
    form = RankingConfigurationForm()
    if request.method == 'POST':
        print request.POST
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
import xlwt
@staff_member_required
def search_contact(request):
    provinces = Province.objects.all()
    companies = Company.objects.all()
    works = Work.objects.all()

    form = ContactSearchForm(request.GET)
    results = []
    if request.GET.has_key('q'):
        print "SEARCH "
        if request.GET.has_key('max_results'):
            results = form.search()[:request.GET.get('max_results')]
        else:
            results = form.search()
    contacts = None
    if len(results)>0:
        contacts = Contact.objects.all().filter(pk__in=[r.pk for r in results])

    return render_to_response('admin/search/search_contact.html', {
        'search_query' : "",
        'contacts' : contacts,
        'form' : form,
        'provinces' : provinces,
        'companies' : companies,
        'works' : works,
        },context_instance=RequestContext(request))

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
        if request.GET.has_key('max_results'):
            results = form.search()[:request.GET.get('max_results')]
        else:
            results = form.search()
    contacts = []
    if len(results)>0:
        contacts = Contact.objects.all().filter(pk__in=[r.pk for r in results])
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