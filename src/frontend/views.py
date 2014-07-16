# Create your views here.
from django.contrib import messages
from django.contrib.messages import get_messages
from django.shortcuts import render_to_response, get_object_or_404
from django.template import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import ModelForm,forms
from django.contrib.auth.models import User
import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from campaigns.models import Event,EventSignup,EventPayment
from contacts.models import Contact,Province,Sector,Work
from django.contrib.localflavor.it.forms import ITSocialSecurityNumberField
from django.contrib.localflavor.it.forms import ITZipCodeField
from django import forms

import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import mimetypes
from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode
from cabinet.models import UserRefFile, UserCertFile

class ContactForm(forms.Form):
    name = forms.CharField(error_messages={'required': 'Inserire il proprio nome'})
    surname = forms.CharField(error_messages={'required': 'Inserire il proprio cognome'})
    sex = forms.CharField(error_messages={'required': 'Selezionare il proprio sesso'})
    birthdate = forms.DateField(error_messages={'required': 'Selezionare la propria data di nascita'})
    email = forms.EmailField(error_messages={'required': 'Inserire la propria email'})
    street = forms.CharField(error_messages={'required': 'Inserire la via del proprio indirizzo'})
    civic = forms.CharField(error_messages={'required': 'Inserire il civico del proprio indirizzo'})
    phone_number = forms.CharField(error_messages={'required': 'Inserire il proprio numero telefonico'})
    city = forms.CharField(error_messages={'required': 'Inserire la citta\''})
    province = forms.IntegerField(error_messages={'required': 'Selezionare la provincia'})
    #sector = forms.IntegerField(error_messages={'required': 'Selezionare il proprio settore lavorativo'})
    work = forms.IntegerField(error_messages={'required': 'Selezionare la propria professione'})
    code = ITSocialSecurityNumberField(error_messages={'required': 'Inserire un codice fiscale valido','invalid':'Inserire un codice fiscale valido'})
    zip = ITZipCodeField(error_messages={'required': 'Inserire un cap valido'})



def test_user(request):
    username = request.GET.get("username")
    import json
    response_data = {}
    check_user = User.objects.all().filter(username=username)
    if check_user:
        response_data['value'] = 'KO'
    else:
        response_data['value'] = 'OK'
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def view_home(request):
    today = datetime.datetime.now()
    events = Event.objects.all().filter(date__gte=today,is_public=True)
    return render_to_response('frontend/home.html', {"events":events},
                              context_instance=RequestContext(request))


@login_required(login_url="/")
def view_signup(request):
    import json
    response_data = {}
    # TODO coupon management
    if request.method == 'POST':
        print request.POST.get("cro")
        print request.user
        print request.user.email
        print request.POST.get("note")
        print request.POST.get("event")
        print request.POST.get("money")
        event = Event.objects.filter(id=request.POST.get("event"))[0]
        contact = Contact.objects.all().filter(owner=request.user)[0]
        if EventSignup.objects.all().filter(event=event,contact=contact):
            response_data["error"] = "L'utente risulta gia' regolarmente iscritto all'evento"
        else:
            print "Non iscritto"
            if not EventPayment.objects.filter(event=event, contact=contact):
                omaggio = False
                relatore = False
                pagante = False
                staff = False
                nota = request.POST.get("note")

                #tODO coupon management
                if request.POST.get("cro") == "00000000000000":
                    omaggio = True
                else:
                    pagante = True

                if not EventSignup.objects.filter(event=event, contact=contact, staff=staff, omaggio=omaggio,
                                                  pagante=pagante, relatore=relatore):
                    signup = EventSignup(event=event, contact=contact, staff=staff, omaggio=omaggio,
                                         pagante=pagante, note=nota,relatore=relatore)
                    signup.save()
                if pagante:		   
                    type = request.POST.get("money") #event.money
                    print "TYPE" + type
                    way = request.POST.get("cro")
                    executor = request.POST.get("ragionesociale")
                    street = request.POST.get("indirizzo")
                    cap = request.POST.get("cap")
                    citta = request.POST.get("citta")
                    province = None
                    if request.POST.get("provincia") != '---':
                        province = Province.objects.filter(id=request.POST.get("provincia"))[0]
                    code = request.POST.get("codefiscale")
                    vat = request.POST.get("piva")
                    payment = EventPayment(event=event, contact=contact, type=type, way=way, executor=executor,
                                           street=street, zip=cap, city=citta, province=province, code=code,
                                           vat=vat)
                    payment.save()

                response_data["success"] = "Iscrizione effettuata. Ti verra' inviata una mail di conferma!"
                sendConfirmation(event,contact)
            else:
                response_data["error"] = "[ERRORE] Problemi nella registrazione. Contattare l'assistenza!!!"
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@login_required(login_url="/")
def view_contact(request):
    import json
    import smtplib
    from email.MIMEText import MIMEText
    from django.conf import settings
    response_data = {}
    if request.method == 'POST':
        print request.POST.get("message")
        print request.user
        print request.user.email
        print request.POST.get("reason")
        to = ('K.Viel@enervit.it',)
        subject = "Richiesta di contatto dal portale NTF"
        s = smtplib.SMTP_SSL(settings.EMAIL_HOST,settings.EMAIL_PORT,'enervit.com')
        msg ="Messaggio dall'utente: "+request.user.username +" ("+request.user.email+")\n\n"
        msg +="Motivo della richiesta: "+request.POST.get("reason")+"\n\n"
        msg +="Messaggio:\n\n"+request.POST.get("message")+"\n\n\n\n";
        msg +="-- Portale NTF"
        mime = MIMEText(msg)
        mime['Subject'] = subject
        s.set_debuglevel(1)
        s.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
        s.sendmail(settings.EMAIL_FROM,to,mime.as_string())
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

@login_required(login_url='/')
def view_main(request):
    contact = Contact.objects.all().filter(owner=request.user)
    provinces = Province.objects.all()
    sectors = Sector.objects.all()
    ref_files = UserRefFile.objects.filter(user=request.user)
    cert_files = UserCertFile.objects.filter(user=request.user)
    form = ContactForm()
    today = datetime.datetime.now()
    events = Event.objects.all().filter(date__gte=today,is_public=True)
    iscrizioni = []
    #print contact
    if len(contact)>0:
        iscrizioni = EventSignup.objects.all().filter(contact=contact[0])
    signups = []
    for s in iscrizioni:
        signups.append(s.event)
    #print signups
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if contact and form.is_valid():
            up_contact = Contact.objects.get(code=contact[0].code)
            province = Province.objects.filter(id=form.cleaned_data["province"])[0]
            work = Work.objects.filter(id=form.cleaned_data["work"])[0]
            up_contact.name=form.cleaned_data["name"]
            up_contact.surname=form.cleaned_data["surname"]
            up_contact.street =  form.cleaned_data["street"]
            up_contact.province = province
            up_contact.birthdate =  form.cleaned_data["birthdate"]
            up_contact.city = form.cleaned_data["city"]
            up_contact.zip = form.cleaned_data["zip"]
            up_contact.civic = form.cleaned_data["civic"]
            up_contact.email = form.cleaned_data["email"]
            up_contact.sex = form.cleaned_data["sex"]
            up_contact.phone_number=form.cleaned_data["phone_number"]
            up_contact.work=work
            up_contact.save()
            messages.success(request, "Informazioni Aggiornate!!")
            return HttpResponseRedirect('/frontend/main')
        elif form.is_valid():
            province = Province.objects.filter(id=form.cleaned_data["province"])[0]
            work = Work.objects.filter(id=form.cleaned_data["work"])[0]

            my_contact = Contact(name=form.cleaned_data["name"], surname=form.cleaned_data["surname"], street=form.cleaned_data["street"], province=province,
                                 birthdate = form.cleaned_data["birthdate"],sex = form.cleaned_data["sex"], city=form.cleaned_data["city"], zip=form.cleaned_data["zip"], civic = form.cleaned_data["civic"], email=form.cleaned_data["email"], phone_number=form.cleaned_data["phone_number"], work=work, code = form.cleaned_data["code"], owner = request.user)
            my_contact.save()
    work_str = "0"
    if contact:
        work_str = str(contact[0].work.id)
    return render_to_response(
        'frontend/main.html',
        {
            "contact": contact,
            "form": form,
            "provinces": provinces,
            "sectors": sectors,
            "events": events,
            "signups": signups,
            "work_str": work_str,
            "ref_files": ref_files,
            "cert_files": cert_files
        },
        context_instance=RequestContext(request)
    )



def sendConfirmation(event,contact):
    to = (contact.email,)
    subject = "Conferma iscrizione Evento "+event.title
    object ="""
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
                    <body>
                    <!--[if (gte mso 9)|(IE)]>
                          <table width="540" align="center" cellpadding="0" cellspacing="0" border="0">
                            <tr>
                              <td>
                    <![endif]-->

                    <table class="content" align="center" cellpadding="0" cellspacing="0" border="0" style="width: 100%; max-width: 540px;">
                      <tr>
                        <td>
                    """
    object += smart_str(event.emailcontent)
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
        object = smart_str(object).replace("[[COGNOME]]",smart_str(contact.surname.capitalize()))
        object = smart_str(object).replace("[[EMAIL]]",smart_str(contact.email.lower()))
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_FROM
        part1 = MIMEText(object,'html')
        msg.attach(part1)
        attachments = event.emailattachment
        if attachments:
            path = "/var/www/yellowpage/media/emailattachments/"+str(event.emailattachment)
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
            attach.add_header('Content-Disposition', 'attachment', filename=str(path).replace("/var/www/yellowpage/media/emailattachments/", ""))
            msg.attach(attach)
        s = smtplib.SMTP_SSL(settings.EMAIL_HOST,settings.EMAIL_PORT,'enervit.com')
        s.set_debuglevel(1)
        s.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
        s.sendmail(settings.EMAIL_FROM,to,msg.as_string())

