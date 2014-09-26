# Create your views here.
# -*- coding: utf-8 -*-

import json
import uuid

from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.context_processors import csrf

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import *
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import ModelForm
from django import forms
from django.views.decorators.http import require_POST
from django.forms.models import inlineformset_factory
from django.conf import settings
from django.utils.encoding import smart_str
from xlrd import open_workbook
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from backend.utils import get_its_users
from campaigns.models import Campaign, Newsletter, Event, Image, NewsletterTemplate, NewsletterAttachment, \
    NewsletterTarget, NewsletterSchedulation, EventSignup, EventPayment, AreaManager, Channel, Theme, Goal, \
    PointOfSaleType, EventCoupon, EventType, ProductGroup, District, is_its, can_handle_events, \
    ITSRelDistrict, ITSRelConsultant
from contacts.models import Contact, Sector, Work, Province, Company
from cabinet.models import EventFile


@csrf_exempt
@require_POST
@staff_member_required
def upload_photos(request):
    images = []
    for f in request.FILES.getlist("file"):
        obj = Image.objects.create(upload=f, is_image=True)
        images.append({"filelink": obj.upload.url})
    return HttpResponse(json.dumps(images), mimetype="application/json")


@staff_member_required
def recent_photos(request):
    images = [
        {"thumb": obj.upload.url, "image": settings.ROOT_URL + obj.upload.url}
        for obj in Image.objects.filter(is_image=True).order_by("-date_created")[:20]
    ]
    return HttpResponse(json.dumps(images), mimetype="application/json")


class CampaignForm(ModelForm):
    class Meta:
        model = Campaign


class NewsletterTargetForm(ModelForm):
    class Meta:
        model = NewsletterTarget


class NewsletterForm(ModelForm):
    class Meta:
        model = Newsletter


NewsletterAttachmentFormSet = inlineformset_factory(Newsletter, NewsletterAttachment, fields=('file',), can_delete=True,
                                                    max_num=3)


class EventForm(ModelForm):
    class Meta:
        model = Event


class NewsletterTemplateForm(ModelForm):
    class Meta:
        model = NewsletterTemplate


class NewsletterSchedulationForm(ModelForm):
    class Meta:
        model = NewsletterSchedulation


class EventSignupForm(ModelForm):

    class Meta:
        model = EventSignup
        exclude = ("coupon",)


class ImportSignup(forms.Form):
    event = forms.IntegerField()
    file = forms.FileField(label="Seleziona file EXCEL da importare")


class SingleSendForm(forms.Form):
    contact = forms.EmailField()
    newsletter = forms.IntegerField()

class AreeManagerForm(ModelForm):
    class Meta:
        model = AreaManager


class ThemeForm(ModelForm):
    class Meta:
        model = Theme


class GoalForm(ModelForm):
    class Meta:
        model = Goal


class ChannelForm(ModelForm):
    class Meta:
        model = Channel


class PointOfSaleTypeForm(ModelForm):
    class Meta:
        model = PointOfSaleType


class EventTypeForm(ModelForm):
    class Meta:
        model = EventType


# TODO TO prune because not used any longer
class EventCouponForm(ModelForm):
    class Meta:
        model = EventCoupon


##########################
####  CAMPAIGN CRUD ######
#########################

@staff_member_required
def view_campaign(request):
    campaigns = Campaign.objects.all()
    return render_to_response('admin/campaigns/view_campaign.html', {'campaigns': campaigns},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_campaign(request):
    c = {}
    c.update(csrf(request))
    form = CampaignForm()
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            new_campaign = form.save()
            if request.POST.has_key('_addanother'):
                form = CampaignForm()
            else:
                messages.success(request, 'Aggiunta campagna \"' + new_campaign.name + '\"')
                return HttpResponseRedirect('/admin/campaigns/campaign')
    c = {'form': form}
    return render_to_response('admin/campaigns/view_add_campaign.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_campaign_details(request, id):
    campaign = get_object_or_404(Campaign, id=id)
    newsletter = Newsletter.objects.all().filter(campaign=campaign)
    events = Event.objects.all().filter(campaign=campaign)
    form = CampaignForm()
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            new_campaign = form.save(commit=False)
            new_campaign.save()
            messages.success(request, 'Campagna \"' + new_campaign.name + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/campaigns/campaign/' + id)
    return render_to_response('admin/campaigns/view_campaign_details.html',
                              {'campaign': campaign, 'newsletter': newsletter, 'events': events, 'form': form},
                              context_instance=RequestContext(request))


##########################
####  NEWSLETTER CRUD ####
##########################


@staff_member_required
def view_newsletter(request):
    newsletter = Newsletter.objects.all()
    return render_to_response('admin/campaigns/view_newsletter.html', {'newsletter': newsletter},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_newsletter(request):
    c = {}
    c.update(csrf(request))
    form = NewsletterForm()
    attachments = NewsletterAttachmentFormSet(instance=Newsletter())
    campaigns = Campaign.objects.all()
    events = Event.objects.all()
    ntemplates = NewsletterTemplate.objects.all()
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            new_newsletter = form.save()
            attachments = NewsletterAttachmentFormSet(request.POST, request.FILES, instance=new_newsletter)
            if attachments:
                attachments.save()
            if request.POST.has_key('_addanother'):
                form = NewsletterForm()
            else:
                if request.POST.get('event') is not None or request.POST.get('event') is not "-1":
                    event = Event.objects.filter(id=request.POST.get('event'))
                    eventSignups = EventSignup.objects.all().filter(event=event)
                    for es in eventSignups:
                        if not NewsletterTarget.objects.filter(newsletter=new_newsletter, contact=es.contact):
                            target = NewsletterTarget(newsletter=new_newsletter, contact=es.contact)
                            target.save()
                messages.success(request, 'Aggiunta newsletter \"' + new_newsletter.name + '\"')
                return HttpResponseRedirect('/admin/campaigns/newsletter')
    c = {'form': form, 'campaigns': campaigns, 'ntemplates': ntemplates, 'attachments': attachments, 'events': events}
    return render_to_response('admin/campaigns/view_add_newsletter.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_newsletter_details(request, id):
    newsletter = get_object_or_404(Newsletter, id=id)
    form = NewsletterForm()
    attachments = NewsletterAttachmentFormSet(instance=newsletter)
    campaigns = Campaign.objects.all()
    events = Event.objects.all()
    ntemplates = NewsletterTemplate.objects.all()
    task = -1
    schedulation_id = -1
    schedulations = NewsletterSchedulation.objects.filter(newsletter=newsletter)
    if schedulations:
        task = 1
        schedulation_id = schedulations[0].id

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        attachments2 = NewsletterAttachmentFormSet(request.POST, request.FILES, instance=newsletter)
        if form.is_valid():
            new_newsletter = form.save(commit=False)
            new_newsletter.save()
            if attachments2.is_valid():
                attachments2.save(commit=False)
                attachments2.save()
            if request.POST.get('event') is not None or request.POST.get('event') is not "-1":
                event = Event.objects.filter(id=request.POST.get('event'))
                eventSignups = EventSignup.objects.all().filter(event=event)
                for es in eventSignups:
                    if not NewsletterTarget.objects.filter(newsletter=new_newsletter, contact=es.contact):
                        target = NewsletterTarget(newsletter=new_newsletter, contact=es.contact)
                        target.save()

            messages.success(request, 'Newsletter \"' + new_newsletter.name + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/campaigns/newsletter/' + id)
    return render_to_response('admin/campaigns/view_newsletter_details.html',
                              {'newsletter': newsletter, 'form': form, 'campaigns': campaigns, 'ntemplates': ntemplates,
                               'attachments': attachments, 'events': events, 'task': task, 'schedulation_id': schedulation_id},
                              context_instance=RequestContext(request))


@staff_member_required
def send_single_newsletter(request):
    newsletters = Newsletter.objects.all()
    contacts = Contact.objects.exclude(email__isnull=True).exclude(email__exact='')
    form = SingleSendForm()
    return render_to_response('admin/campaigns/view_newsletter_singlesend.html',
                              {'form': form, 'newsletters': newsletters, 'contacts': contacts},
                              context_instance=RequestContext(request))


def send_single_email(request):
    newsletter = get_object_or_404(Newsletter, id=request.GET.get("nl"))
    contact = get_object_or_404(Contact, code=request.GET.get("ct"))
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText
    import mimetypes

    to = contact.email
    subject = newsletter.subject
    object = """
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
            <html>
            <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
              <title>Enervit</title>

              <style>
                @media only screen and (min-device-width: 541px) {
                  .content {
                    width: 540px !important;
                  }
                }
              </style>
            </head>
            <body">
            <!--[if (gte mso 9)|(IE)]>
                  <table width="540" align="center" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td>
            <![endif]-->

            <table class="content" align="center" cellpadding="0" cellspacing="0" border="0" style="width: 100%; max-width: 540px;">
              <tr>
                <td>
            """
    object += smart_str(newsletter.content)
    object += """
                     </td>
                  </tr>
                </table>

        <!--[if (gte mso 9)|(IE)]>
              </td>
            </tr>
        </table>
        <![endif]-->

        </body>
        </html>
        """

    if contact:
        object = smart_str(object).replace("[[NOME]]", smart_str(contact.name.capitalize()))
        object = smart_str(object).replace("[[COGNOME]]", smart_str(contact.surname.capitalize()))
        object = smart_str(object).replace("[[EMAIL]]", smart_str(contact.email.lower()))
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_FROM
    part1 = MIMEText(object, 'html')
    msg.attach(part1)
    attachments = NewsletterAttachment.objects.all().filter(newsletter=newsletter)
    if attachments:
        i = 0
        while i < len(attachments):
            path = "/var/www/yellowpage/media/" + str(attachments[i].file)
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                fp = open(path)
                attach = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'image':
                fp = open(path, 'rb')
                attach = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(path, 'rb')
                attach = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(path, 'rb')
                attach = MIMEBase(maintype, subtype)
                attach.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(attach)
            attach.add_header('Content-Disposition', 'attachment',
                              filename=str(path).replace("/var/www/yellowpage/media/attachments/", ""))
            msg.attach(attach)
            i += 1
    s = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, 'enervit.com')
    s.set_debuglevel(1)
    s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    s.sendmail(settings.EMAIL_FROM, to, msg.as_string())
    response_data = {}
    response_data['value'] = 'OK'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@staff_member_required
def test_newsletter(request, id):
    newsletter = get_object_or_404(Newsletter, id=id)

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText
    import mimetypes

    to = (newsletter.testcontact,)
    subject = newsletter.subject
    object = """
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
            <html>
            <head>
              <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
              <title>Enervit</title>

              <style>
                @media only screen and (min-device-width: 541px) {
                  .content {
                    width: 540px !important;
                  }
                }
              </style>
            </head>
            <body">
            <!--[if (gte mso 9)|(IE)]>
                  <table width="540" align="center" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td>
            <![endif]-->

            <table class="content" align="center" cellpadding="0" cellspacing="0" border="0" style="width: 100%; max-width: 540px;">
              <tr>
                <td>
            """
    #object = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
    #object += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="it" lang="it"><head><meta http-equiv="Content-Type" content="text/html; charset="UTF-8" />'
    #object += '<title>Enervit</title><link rel="stylesheet" href="http://localhost:8080/static/admin/css/iframe.css" /></head><body style="background-color: #dcdcdc;">'
    object += smart_str(newsletter.content)
    #object += '</body></html>'
    object += """
                     </td>
                  </tr>
                </table>

        <!--[if (gte mso 9)|(IE)]>
              </td>
            </tr>
        </table>
        <![endif]-->

        </body>
        </html>
        """


    #contact = Contact.objects.all().filter(email=newsletter.testcontact)[0]
    #if contact:
    #    object = smart_str(object).replace("[[NOME]]", smart_str(contact.name.capitalize()))
    #    object = smart_str(object).replace("[[COGNOME]]",smart_str(contact.surname.capitalize()))
    #    object = smart_str(object).replace("[[EMAIL]]",smart_str(contact.email.lower()))
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_FROM
    part1 = MIMEText(object, 'html')
    msg.attach(part1)
    attachments = NewsletterAttachment.objects.all().filter(newsletter=newsletter)
    if attachments:
        i = 0
        while i < len(attachments):
            path = "/var/www/yellowpage/media/" + str(attachments[i].file)
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                fp = open(path)
                attach = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'image':
                fp = open(path, 'rb')
                attach = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(path, 'rb')
                attach = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(path, 'rb')
                attach = MIMEBase(maintype, subtype)
                attach.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(attach)
            attach.add_header('Content-Disposition', 'attachment',
                              filename=str(path).replace("/var/www/yellowpage/media/attachments/", ""))
            msg.attach(attach)
            i += 1
    s = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, 'enervit.com')
    s.set_debuglevel(1)
    s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    s.sendmail(settings.EMAIL_FROM, to, msg.as_string())
    response_data = {}
    response_data['value'] = 'OK'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@staff_member_required
def sendmassive_newsletter(request, id):
    newsletter = get_object_or_404(Newsletter, id=id)
    import time

    time.sleep(15)
    response_data = {}
    response_data['value'] = 'OK'
    response_data['response'] = 'bla bla bla'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def view_unsubscribe(request):
    contact = get_object_or_404(Contact, email=request.GET.get('email'))
    contact.status = 'D'
    contact.save()
    return render_to_response('admin/campaigns/view_newsletter_unsubscribe.html', {},
                              context_instance=RequestContext(request))


##########################################
##### NEWSLETTERSCHEDULATION CRUD ########
##########################################

@staff_member_required
def tasks_newsletter(request):
    schedulations = NewsletterSchedulation.objects.all()
    return render_to_response('admin/campaigns/view_newsletter_schedulations.html', {'schedulations': schedulations},
                              context_instance=RequestContext(request))


@staff_member_required
def add_schedule_newsletter(request):
    c = {}
    c.update(csrf(request))
    newsletters = Newsletter.objects.all().filter(status="W")
    form = NewsletterSchedulationForm()
    if request.method == 'POST':
        form = NewsletterSchedulationForm(request.POST)
        if form.is_valid():
            new_schedulation = form.save()
            if request.POST.has_key('_addanother'):
                form = NewsletterSchedulationForm()
            else:
                messages.success(request, 'Aggiunta schedulazione')
                return HttpResponseRedirect('/admin/campaigns/newsletter/tasks')
    c = {'form': form, 'newsletters': newsletters}
    return render_to_response('admin/campaigns/view_add_newsletterschedulation.html', c,
                              context_instance=RequestContext(request))


@staff_member_required
def schedule_newsletter_details(request, id):
    schedule = get_object_or_404(NewsletterSchedulation, id=id)
    form = NewsletterSchedulationForm()
    newsletters = Newsletter.objects.all().filter(status="W")
    if request.method == 'POST':
        form = NewsletterSchedulationForm(request.POST, instance=schedule)
        if form.is_valid():
            new_schedule = form.save(commit=False)
            new_schedule.save()
            messages.success(request, 'Aggiunta schedulazione')
            return HttpResponseRedirect('/admin/campaigns/newsletter/tasks')
    return render_to_response('admin/campaigns/view_newsletterschedulation_details.html',
                              {'newsletters': newsletters, 'form': form, 'schedule': schedule},
                              context_instance=RequestContext(request))


@staff_member_required
def schedule_newsletter_delete(request, id):
    schedule = get_object_or_404(NewsletterSchedulation, id=id)
    schedule.delete()
    messages.success(request, 'Rimossa schedulazione')
    return HttpResponseRedirect('/admin/campaigns/newsletter/tasks')


##########################
##### EVENT CRUD ########
#########################
@staff_member_required
def view_events(request):
    events = Event.objects.all()
    for e in events:
        e.from_its = '?from_its=1' if e.is_its else ''

    return render_to_response('admin/campaigns/view_event.html', {'events': events},
                              context_instance=RequestContext(request))


@staff_member_required
def view_signups(request):
    events = Event.objects.all()
    return render_to_response('admin/campaigns/view_event_signups.html', {'events': events},
                              context_instance=RequestContext(request))


@staff_member_required
def view_signup_by_event(request, eventid):
    event = Event.objects.get(pk=eventid)
    payments_qs = EventPayment.objects.filter(event=event)
    payments = {str(row.contact): row.way for row in payments_qs}
    signups = EventSignup.objects.all().filter(event=event)
    return render_to_response('admin/campaigns/view_signup_by_event.html', {'signups': signups, 'payments': payments},
                              context_instance=RequestContext(request))


@staff_member_required
def view_signup_details(request, signupid):
    signup = EventSignup.objects.all().filter(id=signupid)[0]
    payment = None
    if signup.pagante:
        payments = EventPayment.objects.all().filter(contact=signup.contact, event=signup.event)
        if len(payments) > 0:
            payment = payments[0]
    print signup
    return render_to_response('admin/campaigns/view_signup_details.html', {'signup': signup, 'payment': payment},
                              context_instance=RequestContext(request))


@staff_member_required
def view_export_signup_by_event(request, eventid):
    response = HttpResponse(mimetype="application/ms-excel")
    event = Event.objects.all().filter(id=eventid)[0]
    response['Content-Disposition'] = 'attachment; filename=esportazione_evento-' + event.__unicode__() + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Foglio 1')

    ws.write(0, 0, 'Staff')
    ws.write(0, 1, 'Omaggio')
    ws.write(0, 2, 'Pagante')
    ws.write(0, 3, 'Cognome')
    ws.write(0, 4, 'Nome')
    ws.write(0, 5, 'Indirizzo')
    ws.write(0, 6, 'CAP')
    ws.write(0, 7, 'Citta\'')
    ws.write(0, 8, 'Prov')
    ws.write(0, 9, 'Regione')
    ws.write(0, 10, 'Email')
    ws.write(0, 11, 'Qualifica')
    ws.write(0, 12, 'Categoria')
    ws.write(0, 13, 'Tel')
    ws.write(0, 14, 'Pagamento')
    ws.write(0, 15, 'Mod. Pag')
    ws.write(0, 16, 'Note')
    ws.write(0, 17, 'Nome')
    ws.write(0, 18, 'Indirizzo')
    ws.write(0, 19, 'Cap')
    ws.write(0, 20, 'Citta\'')
    ws.write(0, 21, 'Prov')
    ws.write(0, 22, 'Iva')
    ws.write(0, 23, 'CF')

    signup = EventSignup.objects.all().filter(event=event)

    row = 1
    for iscrizione in signup:
        staff = ""
        if iscrizione.staff == True:
            staff = "1"
        ws.write(row, 0, staff)
        omaggio = ""
        if iscrizione.omaggio == True:
            omaggio = "1"
        ws.write(row, 1, omaggio)
        pagante = ""
        if iscrizione.pagante == True:
            pagante = "1"
        ws.write(row, 2, pagante)
        ws.write(row, 3, iscrizione.contact.surname.capitalize())
        ws.write(row, 4, iscrizione.contact.name.capitalize())
        ws.write(row, 5, iscrizione.contact.street)
        ws.write(row, 6, iscrizione.contact.zip)
        ws.write(row, 7, iscrizione.contact.city)
        if iscrizione.contact.province:
            ws.write(row, 8, iscrizione.contact.province.code)
            ws.write(row, 9, iscrizione.contact.province.region.name)
        ws.write(row, 10, iscrizione.contact.email)
        if iscrizione.contact.work:
            ws.write(row, 11, iscrizione.contact.work.name.capitalize())
            ws.write(row, 12, iscrizione.contact.work.sector.name.capitalize())
        ws.write(row, 13, iscrizione.contact.phone_number)
        if EventPayment.objects.filter(event=event, contact=iscrizione.contact):
            payment = EventPayment.objects.filter(event=event, contact=iscrizione.contact)[0]
            ws.write(row, 14, payment.type)
            ws.write(row, 15, payment.way)
            ws.write(row, 16, payment.note)
            ws.write(row, 17, payment.executor)
            ws.write(row, 18, payment.street)
            ws.write(row, 19, payment.zip)
            ws.write(row, 20, payment.city)
            if payment.province:
                ws.write(row, 21, payment.province.code)
            ws.write(row, 22, payment.vat)
            ws.write(row, 23, payment.code)
        else:
            ws.write(row, 16, iscrizione.note)
        row += 1
    wb.save(response)
    return response


# @staff_member_required
# @user_passes_test(is_controller)
def _prepare_event_form():
    form = EventForm()
    campaigns = Campaign.objects.all()
    its_users = get_its_users()
    consultants = Contact.objects.filter(type='C')
    districts = District.objects.all()
    consultant_rels = ITSRelConsultant.objects.all()
    its_rels = ITSRelDistrict.objects.all()
    areamanager = AreaManager.objects.all()
    eventtype = EventType.objects.filter(selectable=True)
    channel = Channel.objects.all()
    theme = Theme.objects.all()
    pointofsaletype = PointOfSaleType.objects.all()
    province = Province.objects.all()
    companies = Company.objects.all()
    its_id = district_id = consultant_id = -1
    return areamanager, campaigns, channel, companies, consultant_id, consultant_rels, consultants, district_id, districts, eventtype, form, its_id, its_rels, its_users, pointofsaletype, province, theme


def view_add_event(request):
    c = {}
    from_its = False
    if request.GET.get('from_its'):
        from_its = True
    if not can_handle_events(request.user, new=True, from_its=from_its):
        messages.error(request, 'Non si hanno privilegi sufficienti per aggiungere un evento pubblico')
        if is_its(request.user):
            return redirect('/admin/its/agenda/')
        else:
            return redirect('/admin')
    c.update(csrf(request))

    areamanager, campaigns, channel, companies, \
        consultant_id, consultant_rels, consultants, \
        district_id, districts, eventtype, form, its_id, \
        its_rels, its_users, pointofsaletype, province, theme = _prepare_event_form()

    if request.method == 'POST':
        post_cons_id = request.POST.get('consultant')
        if post_cons_id:
            consultant_id = post_cons_id
            if post_cons_id == '-1':
                request.POST['consultant'] = ''
        form = EventForm(request.POST)
        if form.is_valid():
            new_event = form.save()
            if request.FILES:
                my_file = request.FILES['emailattachment']
                with open('/var/www/yellowpage/media/emailattachments/' + my_file.name, 'wb+') as destination:
                    for chunk in my_file.chunks():
                        destination.write(chunk)
                new_event.emailattachment = my_file.name
                new_event.save()
            messages.success(request, 'Aggiunto Evento \"' + new_event.date.strftime("%d-%m-%Y") + '\"')
            if '_addanother' in request.POST:
                form = EventForm()
            else:
                return HttpResponseRedirect('/admin/campaigns/event')
    c = {'form': form, 'province': province, 'campaigns': campaigns,
         'its_users': its_users, 'consultants': consultants, 'from_its': from_its,
         'districts': districts, 'consultant_rels': consultant_rels, 'its_rels': its_rels,
         'areamanager': areamanager, 'eventtype': eventtype, 'companies': companies,
         'channel': channel, 'theme': theme, 'pointofsaletype': pointofsaletype,
         'its_id': its_id, 'district_id': district_id, 'consultant_id': consultant_id}
    return render_to_response('admin/campaigns/view_add_event.html', c, context_instance=RequestContext(request))


# @staff_member_required
# @user_passes_test(is_controller)
def view_event_details(request, id):
    from_its = False
    if request.GET.get('from_its'):
        from_its = True

    event = get_object_or_404(Event, id=id)
    if not can_handle_events(request.user, e=event, from_its=from_its):
        messages.error(request, "Non si hanno privilegi sufficienti per modificare l'evento {}".format(event.title))
        if is_its(request.user):
            return redirect('/admin/its/agenda/')
        else:
            return redirect('/admin')

    areamanager, campaigns, channel, companies, consultant_id, \
        consultant_rels, consultants, district_id, districts, \
        eventtype, form, its_id, its_rels, its_users, \
        pointofsaletype, province, theme = _prepare_event_form()
    consultant_id = event.consultant.code if event.consultant else '-1'
    its_id = district_id = -1
    if event.its_districtmanager:
        its_id = event.its_districtmanager.id
        district_id = ITSRelDistrict.objects.filter(its=event.its_districtmanager)[0].district.id

    eventfiles = EventFile.objects.filter(event=event)
    if request.method == 'POST':
        post_cons_id = request.POST.get('consultant')
        if post_cons_id:
            consultant_id = post_cons_id
            if post_cons_id == '-1':
                request.POST['consultant'] = ''

        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.save()
            if request.FILES:
                my_file = request.FILES['emailattachment']
                with open('/var/www/yellowpage/media/emailattachments/' + my_file.name, 'wb+') as destination:
                    for chunk in my_file.chunks():
                        destination.write(chunk)
                new_event.emailattachment = my_file.name
                new_event.save()
            if request.POST.get("deleteFile") == "on":
                new_event.emailattachment = None
                new_event.save()
            messages.success(request,
                             'Evento \"' + new_event.date.strftime("%d-%m-%Y") + '\" aggiornato correttamente!')
            if from_its and is_its(request.user):
                return HttpResponseRedirect('/admin/its/agenda/')
            return HttpResponseRedirect('/admin/campaigns/event/' + id)
    c = {'event': event, 'eventfiles': eventfiles, 'form': form, 'province': province,
         'campaigns': campaigns, 'consultants': consultants, 'from_its': from_its,
         'districts': districts, 'consultant_rels': consultant_rels, 'its_rels': its_rels,
         'areamanager': areamanager, 'eventtype': eventtype, 'companies': companies,
         'channel': channel, 'theme': theme, 'pointofsaletype': pointofsaletype,
         'its_id': its_id, 'district_id': district_id, 'consultant_id': consultant_id}
    return render_to_response('admin/campaigns/view_event_details.html',
                              c, context_instance=RequestContext(request))


@staff_member_required
def view_event_import(request):
    form = ImportSignup()
    events = Event.objects.all()
    if request.method == 'POST':
        form = ImportSignup(request.POST, request.FILES)
        my_file = request.FILES['file']
        if form.is_valid():
            with open('/var/www/yellowpage/media/xls/' + my_file.name, 'wb+') as destination:
                for chunk in my_file.chunks():
                    destination.write(chunk)
            xls = open_workbook('/var/www/yellowpage/media/xls/' + my_file.name)
            sheet = xls.sheet_by_index(0)
            for row_index in range(sheet.nrows):
                if row_index > 0:
                    if sheet.cell(row_index, 3).value != "" and sheet.cell(row_index, 4).value != "":
                        cognome = sheet.cell(row_index, 3).value.capitalize() if sheet.cell(row_index,
                                                                                            3).value != "" else ""
                        nome = sheet.cell(row_index, 4).value.capitalize() if sheet.cell(row_index,
                                                                                         4).value != "" else ""

                        qualifica = sheet.cell(row_index, 11).value

                        categoria = sheet.cell(row_index, 12).value
                        sectors = Sector.objects.all()
                        work = Work.objects.all()

                        if len(categoria.strip()) > 2 and not Sector.objects.filter(name=categoria.strip()):
                            new_categoria = Sector(name=categoria.strip().capitalize(),
                                                   description=categoria.strip().capitalize())
                            new_categoria.save()
                        if len(categoria.strip()) > 2 and len(qualifica.strip()) > 2 and not Work.objects.filter(
                                name=qualifica.strip()):
                            my_categoria = Sector.objects.filter(name=categoria.strip().capitalize())[0]
                            if my_categoria:
                                new_qualifica = Work(name=qualifica.strip().capitalize(),
                                                     description=qualifica.strip().capitalize(), sector=my_categoria)
                                new_qualifica.save()
                        indirizzo = sheet.cell(row_index, 5).value.capitalize() if sheet.cell(row_index,
                                                                                              5).value != "" else ""
                        cap = str(int(sheet.cell(row_index, 6).value)) if str(
                            sheet.cell(row_index, 6).value) != ""  else ""
                        citta = sheet.cell(row_index, 7).value.capitalize() if sheet.cell(row_index,
                                                                                          7).value != "" else ""
                        prov = sheet.cell(row_index, 8).value.upper() if sheet.cell(row_index, 8).value != "" else ""
                        email = sheet.cell(row_index, 10).value.lower() if sheet.cell(row_index, 10).value != "" else ""
                        tel = sheet.cell(row_index, 13).value.strip() if sheet.cell(row_index,
                                                                                    13).value.strip() != "" else ""

                        province = Province.objects.filter(code=prov)[0] if Province.objects.filter(code=prov) else None
                        relatore = False
                        staff = False
                        omaggio = False
                        pagante = False
                        nota = ""
                        if not Contact.objects.filter(name=nome, surname=cognome, street=indirizzo, city=citta, zip=cap,
                                                      email=email, phone_number=tel):
                            my_work = Work.objects.filter(name=qualifica.strip())[0] if len(
                                qualifica.strip()) > 2 and len(categoria.strip()) > 2 else None
                            code = str(uuid.uuid4()).replace("-", "")[0:16]
                            my_contact = Contact(name=nome, surname=cognome, street=indirizzo, province=province,
                                                 city=citta, zip=cap, email=email, phone_number=tel, work=my_work,
                                                 code=code)
                            my_contact.save()

                        if len(indirizzo.strip()) > 2 and indirizzo.lower() != "enervit" and indirizzo.lower() != "relatore":
                            print indirizzo
                        else:
                            if indirizzo.lower() == "enervit" and sheet.cell(row_index, 0).value == 1:
                                staff = True
                            elif indirizzo.lower() == "relatore" and sheet.cell(row_index, 0).value == 1:
                                staff = True
                                relatore = True
                        if sheet.cell(row_index, 0).value != 1 and sheet.cell(row_index, 1).value == 1:
                            omaggio = True
                            nota = sheet.cell(row_index, 16).value if sheet.cell(row_index, 16).value != "" else  None
                        elif sheet.cell(row_index, 0).value != 1 and sheet.cell(row_index, 2).value == 1:
                            pagante = True
                        event = Event.objects.filter(id=form.cleaned_data['event'])[0]
                        contact = \
                            Contact.objects.filter(name=nome, surname=cognome, street=indirizzo, city=citta, zip=cap,
                                                   email=email, phone_number=tel)[0]

                        if not EventSignup.objects.filter(event=event, contact=contact, staff=staff, omaggio=omaggio,
                                                          pagante=pagante, relatore=relatore):
                            signup = EventSignup(event=event, contact=contact, staff=staff, omaggio=omaggio,
                                                 pagante=pagante, note=nota, relatore=relatore)
                            signup.save()

                        newsletters = Newsletter.objects.all().filter(event=event)
                        for ns in newsletters:
                            if not NewsletterTarget.objects.filter(newsletter=ns, contact=contact):
                                target = NewsletterTarget(newsletter=ns, contact=contact)
                                target.save()

                        if pagante:
                            type = str(sheet.cell(row_index, 14).value) if str(
                                sheet.cell(row_index, 14).value) != "" else  None
                            way = sheet.cell(row_index, 15).value.capitalize() if sheet.cell(row_index,
                                                                                             15).value != "" else  None
                            executor = sheet.cell(row_index, 17).value.capitalize() if sheet.cell(row_index,
                                                                                                  17).value != "" else  None
                            street = sheet.cell(row_index, 18).value.capitalize() if sheet.cell(row_index,
                                                                                                18).value != "" else  None
                            cap = str(int(sheet.cell(row_index, 19).value)) if str(
                                sheet.cell(row_index, 19).value) != ""  else ""
                            citta = sheet.cell(row_index, 20).value.capitalize() if sheet.cell(row_index,
                                                                                               20).value != "" else ""
                            prov = sheet.cell(row_index, 21).value.upper() if sheet.cell(row_index,
                                                                                         21).value != "" else ""
                            vat = str(sheet.cell(row_index, 22).value) if sheet.cell(row_index, 22).value != "" else ""
                            code = sheet.cell(row_index, 23).value.upper() if sheet.cell(row_index,
                                                                                         23).value != "" else ""
                            province = Province.objects.filter(code=prov)[0] if Province.objects.filter(
                                code=prov) else None
                            if not EventPayment.objects.filter(event=event, contact=contact):
                                payment = EventPayment(event=event, contact=contact, type=type, way=way,
                                                       executor=executor,
                                                       street=street, zip=cap, city=citta, province=province, code=code,
                                                       vat=vat)
                                payment.save()

            events = Event.objects.all()
            return render_to_response('admin/campaigns/view_registro.html', {'events': events},
                                      context_instance=RequestContext(request))
    return render_to_response('admin/campaigns/view_event_import_signup.html', {'form': form, 'events': events},
                              context_instance=RequestContext(request))


# use following properties of event in target dictionary:
# color
# backgroundColor
# borderColor
#http://arshaw.com/fullcalendar/docs/event_data/Event_Object/
def view_eventlist_rest(request):
    events = Event.objects.all()
    import json

    targets_json = []
    for e in events:
        target = {'id': e.id, 'start': str(e.date), 'end': str(e.enddate)}
        if e.enddate is None:
            target['end'] = target['start']
        target['title'] = e.description
        if e.title:
            target['title'] = e.title
        target['campaign'] = e.campaign.name if e.campaign else None
        target['url'] = '/admin/campaigns/event/' + str(e.id)
        if e.is_its:
            target['url'] += '?from_its=1'
            target['backgroundColor'] = 'red'
            target['color'] = 'white'
            target['borderColor'] = 'yellow'
        targets_json.append(target)
    response_data = {'value': 'OK', 'message': 'lista', 'targets': targets_json}
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@staff_member_required
def view_calendar(request):
    return render_to_response('admin/campaigns/view_event_calendar.html', {},
                              context_instance=RequestContext(request))


#####################################
##### NewsletterTemplate CRUD #######
#####################################

@staff_member_required
def view_newslettertemplate(request):
    newslettertemplates = NewsletterTemplate.objects.all()
    return render_to_response('admin/campaigns/view_newslettertemplate.html',
                              {'newslettertemplates': newslettertemplates},
                              context_instance=RequestContext(request))


@staff_member_required
def view_add_newslettertemplate(request):
    c = {}
    c.update(csrf(request))
    form = NewsletterTemplateForm()
    if request.method == 'POST':
        form = NewsletterTemplateForm(request.POST)
        if form.is_valid():
            new_template = form.save()
            if request.POST.has_key('_addanother'):
                form = NewsletterForm()
            else:
                messages.success(request, 'Aggiunto template \"' + new_template.name + '\"')
                return HttpResponseRedirect('/admin/campaigns/newslettertemplate')
    c = {'form': form}
    return render_to_response('admin/campaigns/view_add_newslettertemplate.html', c,
                              context_instance=RequestContext(request))


@staff_member_required
def view_newslettertemplate_details(request, id):
    newslettertemplate = get_object_or_404(NewsletterTemplate, id=id)
    form = NewsletterTemplateForm()
    if request.method == 'POST':
        form = NewsletterTemplateForm(request.POST, instance=newslettertemplate)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.save()
            messages.success(request,
                             'Template \"' + new_event.name + '\" aggiornato correttamente!')
            return HttpResponseRedirect('/admin/campaigns/newslettertemplate/' + id)
    return render_to_response('admin/campaigns/view_newslettertemplate_details.html',
                              {'newslettertemplate': newslettertemplate, 'form': form},
                              context_instance=RequestContext(request))


@staff_member_required
def view_newslettertemplate_rest(request):
    sector = request.GET.get('id', '')
    from django.core import serializers

    json_subcat = serializers.serialize("json", NewsletterTemplate.objects.filter(id=sector))
    return HttpResponse(json_subcat, mimetype="application/javascript")


#####################################
##### NewsletterTarget  CRUD #######
#####################################
@staff_member_required
def view_newslettertarget(request):
    newsletters = Newsletter.objects.all()
    return render_to_response('admin/campaigns/view_newslettertarget.html', {'newsletters': newsletters},
                              context_instance=RequestContext(request))


def view_newslettertarget_add(request, nl):
    c = {}
    newsletter = get_object_or_404(Newsletter, id=nl)
    c.update(csrf(request))
    contacts = Contact.objects.all()
    targets = NewsletterTarget.objects.all().filter(newsletter=newsletter)
    c = {'contacts': contacts, 'targets': targets, 'newsletter': newsletter}
    return render_to_response('admin/campaigns/view_newslettertarget_add.html', c,
                              context_instance=RequestContext(request))


def view_newslettertarget_add_rest(request):
    contactId = request.GET.get('contact', '')
    newsletterId = request.GET.get('newsletter', '')
    contact = get_object_or_404(Contact, email=contactId)
    newsletter = get_object_or_404(Newsletter, id=newsletterId)
    if not NewsletterTarget.objects.filter(contact=contact, newsletter=newsletter):
        target = NewsletterTarget(contact=contact, newsletter=newsletter)
        target.save()

    import json

    response_data = {}
    response_data['value'] = 'OK'
    response_data['contact'] = contactId
    response_data['newsletter'] = newsletter.id
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def view_newslettertarget_remove_rest(request):
    targetId = request.GET.get('target', '')
    target = get_object_or_404(NewsletterTarget, id=targetId)
    target.delete()
    import json

    response_data = {}
    response_data['value'] = 'OK'
    response_data['message'] = 'Cancellato'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def view_newslettertarget_list_rest(request):
    newsletterId = request.GET.get('newsletter', '')
    targets = NewsletterTarget.objects.all().filter(newsletter=newsletterId)
    import json

    targets_json = []
    for i in range(0, len(targets)):
        target = {}
        target['id'] = targets[i].id
        target['contact'] = targets[i].contact.name + " " + targets[i].contact.surname
        target['email'] = targets[i].contact.email
        if targets[i].contact.work is not None:
            target['work'] = targets[i].contact.work.name
        else:
            target['work'] = ""
        action_subdivisions = []
        for sub in targets[i].contact.action_subdivision.all():
            action_subdivisions.append(sub.name)
        target['action_subdivision'] = action_subdivisions
        anagrafic_subdivisions = []
        for sub in targets[i].contact.anagrafic_subdivision.all():
            anagrafic_subdivisions.append(sub.name)
        target['anagrafic_subdivision'] = anagrafic_subdivisions
        target['city'] = targets[i].contact.city
        if targets[i].contact.province is not None:
            target['province'] = targets[i].contact.province.code
        else:
            target['province'] = ""
        targets_json.append(target)

    response_data = {}
    response_data['value'] = 'OK'
    response_data['message'] = 'lista'
    response_data['targets'] = targets_json
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


################################
### EVENTSIGNUP CRUD ##########
###############################

@staff_member_required
def view_registro(request):
    events = Event.objects.all()
    return render_to_response('admin/campaigns/view_registro.html', {'events': events},
                              context_instance=RequestContext(request))


@staff_member_required
def view_presence(request, event):
    c = {}
    c.update(csrf(request))
    signup = EventSignup.objects.all().filter(event=event)
    total = signup.count()
    ptotal = EventSignup.objects.all().filter(event=event, presence=True).count()
    nstaff = EventSignup.objects.all().filter(event=event, staff=True).count()
    pstaff = EventSignup.objects.all().filter(event=event, staff=True, presence=True).count()
    nomaggio = EventSignup.objects.all().filter(event=event, omaggio=True).count()
    pomaggio = EventSignup.objects.all().filter(event=event, omaggio=True, presence=True).count()
    npagante = EventSignup.objects.all().filter(event=event, pagante=True).count()
    ppagante = EventSignup.objects.all().filter(event=event, pagante=True, presence=True).count()
    c = {'signups': signup, 'total': total, 'ptotal': ptotal, 'nstaff': nstaff, 'pstaff': pstaff, 'pomaggio': pomaggio,
         'nomaggio': nomaggio, 'npagante': npagante, 'ppagante': ppagante}
    return render_to_response('admin/campaigns/view_eventpresence.html', c, context_instance=RequestContext(request))


@staff_member_required
def view_presence_rest(request):
    sig_id = request.GET.get('signup', '')
    attr = request.GET.get('presence', '')
    signup = EventSignup.objects.all().filter(id=sig_id)[0]
    attr = request.GET.get('presence', '')
    pres = False
    if attr == 'true':
        pres = True
    signup = EventSignup.objects.all().filter(id=sig_id)[0]
    signup.presence = pres
    signup.save()
    event = signup.event
    total = EventSignup.objects.all().filter(event=event).count()
    ptotal = EventSignup.objects.all().filter(event=event, presence=True).count()
    nstaff = EventSignup.objects.all().filter(event=event, staff=True).count()
    pstaff = EventSignup.objects.all().filter(event=event, staff=True, presence=True).count()
    nomaggio = EventSignup.objects.all().filter(event=event, omaggio=True).count()
    pomaggio = EventSignup.objects.all().filter(event=event, omaggio=True, presence=True).count()
    npagante = EventSignup.objects.all().filter(event=event, pagante=True).count()
    ppagante = EventSignup.objects.all().filter(event=event, pagante=True, presence=True).count()
    import json

    response_data = {}
    response_data['value'] = 'OK'
    response_data['presence'] = attr
    response_data['total'] = total
    response_data['ptotal'] = ptotal
    response_data['nstaff'] = nstaff
    response_data['pstaff'] = pstaff
    response_data['nomaggio'] = nomaggio
    response_data['pomaggio'] = pomaggio
    response_data['npagante'] = npagante
    response_data['ppagante'] = ppagante
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@staff_member_required
def view_export_presence(request, id_event):
    response = HttpResponse(mimetype="application/ms-excel")
    event = Event.objects.all().filter(id=id_event)[0]
    response['Content-Disposition'] = 'attachment; filename=esportazione_evento-' + event.__unicode__() + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Foglio 1')

    ws.write(0, 0, 'Presenza')
    ws.write(0, 1, 'Staff')
    ws.write(0, 2, 'Omaggio')
    ws.write(0, 3, 'Pagante')
    ws.write(0, 4, 'Cognome')
    ws.write(0, 5, 'Nome')
    ws.write(0, 6, 'Indirizzo')
    ws.write(0, 7, 'CAP')
    ws.write(0, 8, 'Citta\'')
    ws.write(0, 9, 'Prov')
    ws.write(0, 10, 'Regione')
    ws.write(0, 11, 'Email')
    ws.write(0, 12, 'Qualifica')
    ws.write(0, 13, 'Categoria')
    ws.write(0, 14, 'Tel')
    ws.write(0, 15, 'Pagamento')
    ws.write(0, 16, 'Mod. Pag')
    ws.write(0, 17, 'Note')
    ws.write(0, 18, 'Nome')
    ws.write(0, 19, 'Indirizzo')
    ws.write(0, 20, 'Cap')
    ws.write(0, 21, 'Citta\'')
    ws.write(0, 22, 'Prov')
    ws.write(0, 23, 'Iva')
    ws.write(0, 24, 'CF')

    signup = EventSignup.objects.all().filter(event=event)

    row = 1
    for iscrizione in signup:
        presenza = ""
        if iscrizione.presence == True:
            presenza = '1'
        ws.write(row, 0, presenza)
        staff = ""
        if iscrizione.staff == True:
            staff = "1"
        ws.write(row, 1, staff)
        omaggio = ""
        if iscrizione.omaggio == True:
            omaggio = "1"
        ws.write(row, 2, omaggio)
        pagante = ""
        if iscrizione.pagante == True:
            pagante = "1"
        ws.write(row, 3, pagante)
        ws.write(row, 4, iscrizione.contact.surname.capitalize())
        ws.write(row, 5, iscrizione.contact.name.capitalize())
        ws.write(row, 6, iscrizione.contact.street)
        ws.write(row, 7, iscrizione.contact.zip)
        ws.write(row, 8, iscrizione.contact.city)
        if iscrizione.contact.province:
            ws.write(row, 9, iscrizione.contact.province.code)
            ws.write(row, 10, iscrizione.contact.province.region.name)
        ws.write(row, 11, iscrizione.contact.email)
        if iscrizione.contact.work:
            ws.write(row, 12, iscrizione.contact.work.name.capitalize())
            ws.write(row, 13, iscrizione.contact.work.sector.name.capitalize())
        ws.write(row, 14, iscrizione.contact.phone_number)
        if EventPayment.objects.filter(event=event, contact=iscrizione.contact):
            payment = EventPayment.objects.filter(event=event, contact=iscrizione.contact)[0]
            ws.write(row, 15, payment.type)
            ws.write(row, 16, payment.way)
            ws.write(row, 17, payment.note)
            ws.write(row, 18, payment.executor)
            ws.write(row, 19, payment.street)
            ws.write(row, 20, payment.city)
            ws.write(row, 21, payment.city)
            ws.write(row, 22, payment.province.code)
            ws.write(row, 23, payment.vat)
            ws.write(row, 24, payment.code)
        else:
            ws.write(row, 17, iscrizione.note)
        row += 1
    wb.save(response)
    return response


@staff_member_required
def view_add_eventsignup(request):
    c = {}
    c.update(csrf(request))
    contacts = Contact.objects.all()
    events = Event.objects.all()
    form = EventSignupForm()
    if request.method == 'POST':
        request.POST['omaggio'] = False
        request.POST['pagante'] = False
        request.POST['staff'] = False
        if 'tipo_partecipante' in request.POST:
            request.POST[request.POST['tipo_partecipante']] = True
        form = EventSignupForm(request.POST)
        if form.is_valid():
            new_signup = form.save()
            messages.success(request, 'Aggiunto partecipante {} {} '.format(new_signup.contact.name, new_signup.contact.surname))
            if request.POST.has_key('_addanother'):
                form = EventSignupForm()
                c = {'form': form, 'events': events, 'contacts': contacts}
                return render_to_response('admin/campaigns/view_add_eventsignup.html', c, context_instance=RequestContext(request))
            return HttpResponseRedirect('/admin/campaigns/event')
        else:
            messages.error(request, "Errore nell'aggiunta di un partecipante")
    c = {'form': form, 'events': events, 'contacts': contacts}
    return render_to_response('admin/campaigns/view_add_eventsignup.html', c, context_instance=RequestContext(request))


###########################
##### District ############
###########################

class DistrictForm(ModelForm):
    class Meta:
        model = District

@user_passes_test(lambda u: u.is_superuser)
def view_district(request):
    districts = District.objects.all()
    return render_to_response('admin/campaigns/view_district.html', {'districts': districts},
                              context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_superuser)
def view_district_details(request, id):
    district = get_object_or_404(District, id=id)
    params = {
        'action': "edit",
        'its_users': get_its_users(),
        'district_manager': district.district_manager
    }

    if request.method == "POST":
        form = DistrictForm(request.POST, instance=district)
        action = request.POST.get("action")
        if form.is_valid():
            if action == "edit":
                district = form.save()
                action_message = "Distretto '%s' aggiornato correttamente!" % district.description
            elif action == "delete":
                action_message = "Distretto '%s' cancellato!" % district.description
                district.delete()

            messages.success(request, action_message)
            return HttpResponseRedirect('/admin/campaigns/district/')
    else:
        form = DistrictForm(instance=district)
    params["form"] = form

    return render_to_response('admin/campaigns/view_district_details.html',params,context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_superuser)
def view_district_add(request):
    params = {
        'action': "add",
        'its_users': get_its_users(),
    }

    if request.method == "POST":
        form = DistrictForm(request.POST)
        if form.is_valid():
            district = form.save()
            messages.success(request, "Aggiunta distretto '%s'" % district.description)
            return HttpResponseRedirect('/admin/campaigns/district/')
    else:
        form = DistrictForm()
    params["form"] = form

    return render_to_response('admin/campaigns/view_district_details.html',params,context_instance=RequestContext(request))


###############################
##### AREE MANAGER ############
###############################

@user_passes_test(lambda u: u.is_superuser)
def view_areemanager(request):
    areemanager = AreaManager.objects.all()
    return render_to_response('admin/campaigns/view_areemanager.html', {'areemanager': areemanager},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_add_areemanager(request):
    c = {}
    c.update(csrf(request))
    form = AreeManagerForm()
    if request.method == 'POST':
        form = AreeManagerForm(request.POST)
        if form.is_valid():
            new_area = form.save()
            if request.POST.has_key('_addanother'):
                form = AreeManagerForm()
                messages.success(request, 'Aggiunta area \"' + new_area.name + ' ' + new_area.surname + '\"')
            else:
                messages.success(request, 'Aggiunta area \"' + new_area.name + ' ' + new_area.surname + '\"')
                return HttpResponseRedirect('/admin/campaigns/areamanager')
    c = {'form': form}
    return render_to_response('admin/campaigns/view_add_areemanager.html', c, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_areemanager_details(request, id):
    area = get_object_or_404(AreaManager, id=id)
    form = AreeManagerForm()
    if request.method == 'POST':
        form = AreeManagerForm(request.POST, instance=area)
        if form.is_valid():
            new_area = form.save(commit=False)
            new_area.save()
            messages.success(request,
                             'Area \"' + new_area.name + ' ' + new_area.surname + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/campaigns/areamanager')
    return render_to_response('admin/campaigns/view_areemanager_details.html', {'areamanager': area, 'form': form},
                              context_instance=RequestContext(request))


###############################
##### THEME ###################
###############################

@user_passes_test(lambda u: u.is_superuser)
def view_theme(request):
    themes = Theme.objects.all()
    return render_to_response('admin/campaigns/view_theme.html', {'themes': themes},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_add_theme(request):
    c = {}
    c.update(csrf(request))
    form = ThemeForm()
    if request.method == 'POST':
        form = ThemeForm(request.POST)
        if form.is_valid():
            new_theme = form.save()
            if request.POST.has_key('_addanother'):
                form = ThemeForm()
                messages.success(request, 'Aggiunto tema \"' + new_theme.description + '\"')
            else:
                messages.success(request, 'Aggiunto tema \"' + new_theme.description + '\"')
                return HttpResponseRedirect('/admin/campaigns/theme')
    c = {'form': form}
    return render_to_response('admin/campaigns/view_add_theme.html', c, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_theme_details(request, id):
    theme = get_object_or_404(Theme, id=id)
    form = ThemeForm()
    if request.method == 'POST':
        form = ThemeForm(request.POST, instance=theme)
        if form.is_valid():
            new_theme = form.save(commit=False)
            new_theme.save()
            messages.success(request, 'Tema \"' + new_theme.description + '\" aggiornato correttamente!')
            return HttpResponseRedirect('/admin/campaigns/theme')
    return render_to_response('admin/campaigns/view_theme_details.html', {'theme': theme, 'form': form},
                              context_instance=RequestContext(request))


###############################
##### GOAL ###################
###############################

@user_passes_test(lambda u: u.is_superuser)
def view_goal(request):
    goals = Goal.objects.all()
    return render_to_response('admin/campaigns/view_goal.html', {'goals': goals},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_add_goal(request):
    c = {}
    c.update(csrf(request))
    form = GoalForm()
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            new_goal = form.save()
            if request.POST.has_key('_addanother'):
                form = GoalForm()
                messages.success(request, 'Aggiunto obiettivo \"' + new_goal.description + '\"')
            else:
                messages.success(request, 'Aggiunto obiettivo \"' + new_goal.description + '\"')
                return HttpResponseRedirect('/admin/campaigns/goal')
    c = {'form': form}
    return render_to_response('admin/campaigns/view_add_goal.html', c, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_goal_details(request, id):
    goal = get_object_or_404(Goal, id=id)
    form = GoalForm()
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            new_goal = form.save(commit=False)
            new_goal.save()
            messages.success(request, 'Obiettivo \"' + new_goal.description + '\" aggiornato correttamente!')
            return HttpResponseRedirect('/admin/campaigns/goal')
    return render_to_response('admin/campaigns/view_goal_details.html', {'goal': goal, 'form': form},
                              context_instance=RequestContext(request))


###############################
##### CHANNEL #################
###############################

@user_passes_test(lambda u: u.is_superuser)
def view_channel(request):
    channels = Channel.objects.all()
    return render_to_response('admin/campaigns/view_channel.html', {'channels': channels},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_add_channel(request):
    c = {}
    c.update(csrf(request))
    form = ChannelForm()
    if request.method == 'POST':
        form = ChannelForm(request.POST)
        if form.is_valid():
            new_channel = form.save()
            if request.POST.has_key('_addanother'):
                form = ChannelForm()
                messages.success(request, 'Aggiunto canale \"' + new_channel.description + '\"')
            else:
                messages.success(request, 'Aggiunto canale \"' + new_channel.description + '\"')
                return HttpResponseRedirect('/admin/campaigns/channel')
    c = {'form': form}
    return render_to_response('admin/campaigns/view_add_channel.html', c, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_channel_details(request, id):
    channel = get_object_or_404(Channel, id=id)
    form = ChannelForm()
    if request.method == 'POST':
        form = ChannelForm(request.POST, instance=channel)
        if form.is_valid():
            new_channel = form.save(commit=False)
            new_channel.save()
            messages.success(request, 'Canale \"' + new_channel.description + '\" aggiornato correttamente!')
            return HttpResponseRedirect('/admin/campaigns/channel')
    return render_to_response('admin/campaigns/view_channel_details.html', {'channel': channel, 'form': form},
                              context_instance=RequestContext(request))


###############################
##### POINTOFSALETYPE #########
###############################

@user_passes_test(lambda u: u.is_superuser)
def view_pointofsaletype(request):
    pos = PointOfSaleType.objects.all()
    return render_to_response('admin/campaigns/view_pos.html', {'poses': pos},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_add_pointofsaletype(request):
    c = {}
    c.update(csrf(request))
    form = PointOfSaleTypeForm()
    if request.method == 'POST':
        form = PointOfSaleTypeForm(request.POST)
        if form.is_valid():
            new_pos = form.save()
            if request.POST.has_key('_addanother'):
                form = PointOfSaleTypeForm()
                messages.success(request, 'Aggiunta nuova tipologia punto vendita \"' + new_pos.description + '\"')
            else:
                messages.success(request, 'Aggiunta nuova tipologia punto vendita \"' + new_pos.description + '\"')
                return HttpResponseRedirect('/admin/campaigns/pointofsaletype')
    c = {'form': form}
    return render_to_response('admin/campaigns/view_add_pos.html', c, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_pointofsaletype_details(request, id):
    pos = get_object_or_404(PointOfSaleType, id=id)
    form = PointOfSaleTypeForm()
    if request.method == 'POST':
        form = PointOfSaleTypeForm(request.POST, instance=pos)
        if form.is_valid():
            new_pos = form.save(commit=False)
            new_pos.save()
            messages.success(request, 'Tipologia \"' + new_pos.description + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/campaigns/pointofsaletype')
    return render_to_response('admin/campaigns/view_pos_details.html', {'pos': pos, 'form': form},
                              context_instance=RequestContext(request))


###############################
##### EVENT TYPE   ############
###############################

@user_passes_test(lambda u: u.is_superuser)
def view_eventtype(request):
    eventtypes = EventType.objects.all()
    return render_to_response('admin/campaigns/view_eventtype.html', {'eventtypes': eventtypes},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_add_eventtype(request):
    if request.method == 'POST':
        form = EventTypeForm(request.POST)
        if form.is_valid():
            new_type = form.save()
            if request.POST.has_key('_addanother'):
                form = EventTypeForm()
                messages.success(request, 'Aggiunta nuova tipologia evento \"' + new_type.description + '\"')
            else:
                messages.success(request, 'Aggiunta nuova tipologia evento \"' + new_type.description + '\"')
                return HttpResponseRedirect('/admin/campaigns/eventtype')
    else:
        form = EventTypeForm()
    return render_to_response('admin/campaigns/view_add_eventtype.html', {'form': form},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_eventtype_details(request, id):
    eventtype = get_object_or_404(EventType, id=id)
    form = EventTypeForm(instance=eventtype)
    if request.method == 'POST':
        form = EventTypeForm(request.POST, instance=eventtype)
        if form.is_valid():
            new_type = form.save(commit=False)
            new_type.save()
            messages.success(request, 'Tipologia \"' + new_type.description + '\" aggiornata correttamente!')
            return HttpResponseRedirect('/admin/campaigns/eventtype')
    return render_to_response('admin/campaigns/view_eventtype_details.html', {'eventtype': eventtype, 'form': form},
                              context_instance=RequestContext(request))

###############################
##### EVENTCOUPON  ############
###############################

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def view_eventcoupon_restgenerate(request):
    import json

    response_data = {}
    if request.method == 'POST':
        id = request.POST.get("event_id")
        event = get_object_or_404(Event, id=id)
        codes = request.POST.getlist("codes[]")

        for code in codes:
            if not EventCoupon.objects.filter(coupon=code):
                omaggio = EventCoupon(event=event, coupon=code, used=False)
                omaggio.save()
            else:
                print "coupon esistente"
        response_data['value'] = 'OK'
    else:
        response_data['value'] = 'NAK'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


###############################
##### PRODUCTGROUP  ###########
###############################
class ProductGroupForm(ModelForm):
    sell_in_alloc = forms.DecimalField(localize=True, label='Percentuale sell in')
    sell_in_amount = forms.DecimalField(localize=True, label='Valore sell in')

    class Meta:
        model = ProductGroup


@user_passes_test(lambda u: u.is_superuser)
def view_productgroup(request):
    productgroups = ProductGroup.objects.all()
    return render_to_response('admin/campaigns/view_productgroup.html', {'productgroups': productgroups},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_productgroup_details(request, id):
    if id is None:
        action = "add"
        productgroup = None
    else:
        productgroup = get_object_or_404(ProductGroup, id=id)
        action = "edit"

    if request.method == 'POST':
        if request.POST.get("action") == "delete":
            messages.success(request, 'Tipologia \"' + productgroup.description + '\" cancellato!')
            productgroup.delete()
            return HttpResponseRedirect('/admin/campaigns/productgroup')
        else:
            form = ProductGroupForm(request.POST, instance=productgroup)
            if form.is_valid():
                new_type = form.save(commit=False)
                new_type.save()
                messages.success(request, 'Tipologia \"' + new_type.description + '\" aggiornata correttamente!')
                return HttpResponseRedirect('/admin/campaigns/productgroup')
    else:
        if action == "add":
            form = ProductGroupForm()
        else:
            form = ProductGroupForm(instance=productgroup)

    return render_to_response('admin/campaigns/view_productgroup_details.html',
                              {'productgroup': productgroup, 'form': form, 'action': action},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def view_add_productgroup(request):
    return view_productgroup_details(request, None)


########################
### REST ###############
########################

def view_rest_counter(request):
    campaigns = Campaign.objects.all()
    from contacts.models import Contact

    contacts = Contact.objects.all()
    events = Event.objects.all()
    from survey.models import Survey

    surveys = Survey.objects.all()
    newsletters = Newsletter.objects.all()
    import json

    response_data = {}
    response_data['value'] = 'OK'
    response_data['campaigns_counter'] = len(campaigns)
    response_data['contacts_counter'] = len(contacts)
    response_data['events_counter'] = len(events)
    response_data['newsletters_counter'] = len(newsletters)
    response_data['surveys_counter'] = len(surveys)
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


###########################
######### 404 #############
###########################

def view_404(request):
    response = render_to_response('admin/404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


from forms import CampaignSearchForm, NewsletterSearchForm, EventSearchForm
import xlwt


@staff_member_required
def search_campaign(request):
    form = CampaignSearchForm(request.GET)
    results = []
    if request.GET.has_key('q'):
        results = form.search()
    campaigns = None
    if len(results) > 0:
        campaigns = Campaign.objects.filter(pk__in=[r.pk for r in results])
        campaigns = campaigns[:int(request.GET.get('max_results', 10000))]

    return render_to_response('admin/search/search_campaign.html', {
        'search_query': "",
        'campaigns': campaigns,
        'form': form,
    }, context_instance=RequestContext(request))


@staff_member_required
def search_campaign_export(request):
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=esportazione_ricerca_campagna.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Foglio 1')
    ws.write(0, 0, 'Identificativo')
    ws.write(0, 1, 'Nome')
    ws.write(0, 2, 'Descrizione')
    ws.write(0, 3, 'Data di Inizio')
    ws.write(0, 4, 'Data di Fine')
    ws.write(0, 5, 'Status')
    ws.write(0, 6, 'Newsletter')
    ws.write(0, 7, 'Eventi')

    form = CampaignSearchForm(request.GET)
    results = []
    if request.GET.has_key('q'):
        results = form.search()

    if len(results) > 0:
        campaign = []
        max_results = int(request.GET.get('max_results', 10000))
        for r in results:
            if r is not None and r.model_name == 'contact':
                campaign.append(r.object)
                if len(campaign) >= max_results:
                    break
        row = 1
        for c in campaign:
            ws.write(row, 0, c.id)
            ws.write(row, 1, c.name)
            ws.write(row, 2, c.description)
            ws.write(row, 3, c.startdate.strftime("%d/%m/%Y"))
            ws.write(row, 4, c.enddate.strftime("%d/%m/%Y"))
            if c.status == 'A':
                ws.write(row, 5, "Attiva")
            if c.status == 'N':
                ws.write(row, 5, "Non Attiva")
            if c.status == 'C':
                ws.write(row, 5, "Conclusa")
            if c.status == 'D':
                ws.write(row, 5, "Cancellata")
            newsletter = ""
            for nl in Newsletter.objects.all().filter(campaign=c):
                newsletter += nl.name + " - "
            ws.write(row, 6, newsletter)
            event = ""
            for ev in Event.objects.all().filter(campaign=c):
                if ev.title:
                    desc = ev.title
                else:
                    desc = ev.description
                event += desc + " - "
            ws.write(row, 7, event)
            row += 1
    wb.save(response)
    return response


@staff_member_required
def search_newsletter(request):
    form = NewsletterSearchForm(request.GET)
    events = Event.objects.all()
    campaigns = Campaign.objects.all()
    results = []
    if request.GET.has_key('q'):
        results = form.search()
    newsletters = None

    if len(results) > 0:
        newsletters = []
        max_results = int(request.GET.get('max_results', 10000))
        for r in results:
            if r is not None and r.model_name == 'newsletter':
                newsletters.append(r.object)
                if len(newsletters) >= max_results:
                    break

    return render_to_response('admin/search/search_newsletter.html', {
        'search_query': "",
        'newsletters': newsletters,
        'form': form,
        'events': events,
        'campaigns': campaigns,
    }, context_instance=RequestContext(request))


@staff_member_required
def search_newsletter_export(request):
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=esportazione_ricerca_newsletter.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Foglio 1')
    ws.write(0, 0, 'Identificativo')
    ws.write(0, 1, 'Nome')
    ws.write(0, 2, 'Descrizione')
    ws.write(0, 3, 'Data di Inizio')
    ws.write(0, 4, 'Data di Fine')
    ws.write(0, 5, 'Campagna')
    ws.write(0, 6, 'Evento')
    ws.write(0, 7, 'Status')

    form = NewsletterSearchForm(request.GET)
    results = []
    if request.GET.has_key('q'):
        results = form.search()
    if len(results) > 0:
        valid_results = []
        max_results = int(request.GET.get('max_results', 10000))
        for r in results:
            if r != None and r.model_name == 'newsletter':
                valid_results.append(r.object)
                if len(valid_results) >= max_results:
                    break
        row = 1
        for c in valid_results:
            ws.write(row, 0, c.id)
            ws.write(row, 1, c.name)
            ws.write(row, 2, c.description)
            ws.write(row, 3, c.startdate.strftime("%d/%m/%Y"))
            ws.write(row, 4, c.enddate.strftime("%d/%m/%Y"))
            ws.write(row, 5, c.campaign.name)
            if c.event.title:
                event = c.event.title
            else:
                event = c.event.description
            ws.write(row, 6, event)
            if c.status == 'D':
                ws.write(row, 7, "Bozza")
            if c.status == 'W':
                ws.write(row, 7, "In Attesa di Invio")
            if c.status == 'S':
                ws.write(row, 5, "Invio in Corso")
            if c.status == 'F':
                ws.write(row, 7, "Inviata")
            if c.status == 'C':
                ws.write(row, 7, "Cancellata")
            row += 1
    wb.save(response)
    return response


@staff_member_required
def search_event(request):

    areamanagers, campaigns, channels, companies, \
        consultant_id, consultant_rels, consultants, \
        district_id, districts, eventtypes, form, its_id, \
        its_rels, its, pointofsaletypes, province, themes = _prepare_event_form()

    form = EventSearchForm(request.GET)
    results = []
    if 'q' in request.GET:
        results = form.search()
    events = None
    if len(results) > 0:
        valid_results = []
        max_results = int(request.GET.get('max_results', 10000))
        for r in results:
            if r is not None and r.model_name == 'event':
                valid_results.append(r.object)
                if len(valid_results) >= max_results:
                    break
        events = valid_results

    return render_to_response('admin/search/search_event.html', {
        'search_query': "",
        'events': events,
        'form': form,
        'its': its,
        'districts': districts, 'consultants': consultants,
        'areamanagers': areamanagers,
        'themes': themes,
        'pointofsaletypes': pointofsaletypes,
        'eventtypes': eventtypes,
        'channels': channels,
        'campaigns': campaigns,
        'provinces': province,
    }, context_instance=RequestContext(request))


@staff_member_required
def search_event_export(request):
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=esportazione_ricerca_eventi.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Foglio 1')
    ws.write(0, 0, 'Identificativo')
    ws.write(0, 1, 'Titolo')
    ws.write(0, 2, 'Descrizione')
    ws.write(0, 3, 'Tipo Evento')
    ws.write(0, 4, 'Canale')
    ws.write(0, 5, 'Tema')
    ws.write(0, 6, 'Data')
    ws.write(0, 7, 'Data due')
    ws.write(0, 8, 'Campagna')
    ws.write(0, 9, "Localita\' e indirizzo")
    ws.write(0, 10, 'Provincia')
    ws.write(0, 11, 'Codice Punto Vendita')
    ws.write(0, 12, 'Nominativo Punto Vendita')
    ws.write(0, 13, 'Tipo Punto Vendita')
    ws.write(0, 14, 'Formatore')
    ws.write(0, 15, 'Consultant')
    ws.write(0, 16, 'ITS')
    ws.write(0, 17, 'Area Manager')
    ws.write(0, 18, 'Feedback')
    ws.write(0, 19, 'Presenti')

    form = EventSearchForm(request.GET)
    results = []
    if request.GET.has_key('q'):
        results = form.search()
    if len(results) > 0:
        valid_results = []
        max_results = int(request.GET.get('max_results', 10000))
        for r in results:
            if r is not None and r.model_name == 'event':
                valid_results.append(r.object)
                if len(valid_results) >= max_results:
                    break
        row = 1
        for c in valid_results:
            its = c.its_districtmanager.get_full_name() if c.its_districtmanager else None
            consultant = c.consultant.full_name if c.consultant else None
            campaign = c.campaign.name if c.campaign else None
            ws.write(row, 0, str(c.id))
            ws.write(row, 1, c.title)
            ws.write(row, 2, c.description)
            ws.write(row, 3, str(c.eventtype))
            ws.write(row, 4, str(c.channel))
            ws.write(row, 5, str(c.theme))
            ws.write(row, 6, c.date.strftime("%d/%m/%Y"))
            if c.enddate:
                ws.write(row, 7, c.enddate.strftime("%d/%m/%Y"))
            ws.write(row, 8, campaign)
            ws.write(row, 9, c.place)
            ws.write(row, 10, str(c.province))
            ws.write(row, 11, c.pointofsale)
            ws.write(row, 12, c.pointofsaledescription)
            ws.write(row, 13, str(c.typepointofsale or ''))
            ws.write(row, 14, c.trainer)
            ws.write(row, 15, consultant)
            ws.write(row, 16, its)
            ws.write(row, 17, str(c.areamanager))
            signups = EventSignup.objects.all().filter(event=c, presence=True).count()
            ws.write(row, 18, str(c.feedback or ''))
            ws.write(row, 19, str(signups))
            row += 1
    wb.save(response)
    return response
