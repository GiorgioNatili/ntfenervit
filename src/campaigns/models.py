import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from redactor.fields import RedactorField

from django.contrib.auth.models import User
from contacts.models import Contact

from backend.utils import is_its as is_its_util
# Create your models here.

CAMPAIGN_STATUS = (
    ('A', 'Attiva'),
    ('N', 'Non Attiva'),
    ('C', 'Conclusa'),
    ('D', 'Cancellata'),
)

NEWSLETTER_STATUS = (
    ('D','Bozza'),
    ('W','In attesa di invio'),
    ('S','Invio in corso'),
    ('F','Inviata'),
    ('C','Cancellata')
)

SCHEDULATION_STATUS = (
    ('W','In attesa di invio'),
    ('S','Invio in corso'),
    ('F','Inviata'),
    ('C','Cancellata')
)

class NewsletterSchedulation(models.Model):
    newsletter = models.ForeignKey('campaigns.Newsletter',blank=False,null=False,verbose_name="Newsletter")
    send_date = models.DateTimeField(verbose_name='Data di invio')
    report_email = models.EmailField(verbose_name='Email di report')
    status = models.CharField(max_length=1, choices=SCHEDULATION_STATUS, default='W', verbose_name='Stato')
    def __unicode__(self):
        return '%s %s' %(self.newsletter, self.send_date.strftime("%d-%m-%Y"))
    class Meta:
        verbose_name = "Schedulazione Newsletter"
        verbose_name_plural = "Schedulazioni Newsletter"


class NewsletterTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False, verbose_name='Nome',error_messages={'unique':"Nome gia' presente in anagrafica"})
    content = RedactorField(verbose_name="Template")
    def __unicode__(self):
        return '%s' %(self.name)

    class Meta:
        verbose_name = "Template newsletter"
        verbose_name_plural = "Template newsletter"

class Image(models.Model):
    upload = models.FileField(upload_to="uploads/%Y/%m/%d/")
    date_created = models.DateTimeField(default=datetime.datetime.now)
    is_image = models.BooleanField(default=True)

class NewsletterTarget(models.Model):
    newsletter = models.ForeignKey('campaigns.Newsletter',blank=False,null=False,verbose_name="Newsletter")
    contact = models.ForeignKey('contacts.Contact',blank=False,null=False,verbose_name="Contatto")
    def __unicode__(self):
        return '%s %s' % (self.newsletter, self.contact)

    class Meta:
        verbose_name = "Destinario newsletter"
        verbose_name_plural = "Destinatari newsletter"


class NewsletterAttachment(models.Model):
    newsletter = models.ForeignKey('campaigns.Newsletter')
    file = models.FileField(upload_to='attachments')
    description = models.CharField(max_length=100, blank=True,null=True,verbose_name=u'Descrizione del file')
    def __unicode__(self):
        return '%s' % self.description
    class Meta:
        verbose_name = "Allegato"
        verbose_name_plural = "Allegati"


class Newsletter(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False, verbose_name='Nome',error_messages={'unique':"Nome gia' presente in anagrafica"})
    slug = models.SlugField(max_length=100, unique=True,help_text=u'Campo automatico, non modificare')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrizione')
    subject = models.CharField(max_length=100, blank=True, null=True, verbose_name='Subject')
    startdate = models.DateField(verbose_name='Data di inizio')
    enddate = models.DateField(verbose_name='Data di fine')
    campaign = models.ForeignKey("campaigns.Campaign",verbose_name="Campagna")
    content = RedactorField(verbose_name="Contenuto")
    status = models.CharField(max_length=1, choices=NEWSLETTER_STATUS, default='D', verbose_name='Stato')
    testcontact = models.EmailField(verbose_name='Email di test')
    event = models.ForeignKey('campaigns.Event',blank=True,null=True,verbose_name="Evento di riferimento",error_messages={'null': 'Selezionare un Evento valido!'})
    author = models.ForeignKey(User, null=True, blank=True)
    def __unicode__(self):
        return '%s' % (self.name)

    class Meta:
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletter'

class Survey(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False, verbose_name='Nome',error_messages={'unique':"Nome gia' presente in anagrafica"})
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrizione')
    newsletter = models.ForeignKey("campaigns.Newsletter",verbose_name="Newsletter")

    def __unicode__(self):
        return '%s' % (self.name)

    class Meta:
        verbose_name = 'Questionario'
        verbose_name_plural = 'Questionari'

#ToDo: [REF-AREAITS] Drop AreaITS model; Drop Event.districtmanager FK as it is replaced by Event.its_districtmanager
class AreaIts(models.Model):
    description = models.CharField(max_length=250,blank=False,null=False,verbose_name="Nome Area")

    def __unicode__(self):
        return '%s' % (self.description)

    class Meta:
        verbose_name = "Area ITS"
        verbose_name_plural = "Aree ITS"

class AreaManager(models.Model):
    name = models.CharField(max_length=250,blank=False,null=False,verbose_name="Nome")
    surname = models.CharField(max_length=250,blank=False, null=False,verbose_name="Cognome")

    def __unicode__(self):
        return '%s %s' % (self.name,self.surname)

    class Meta:
        verbose_name = "Area manager"
        verbose_name_plural = "Area manager"

class Theme(models.Model):
    description = models.CharField(max_length=250,blank=False, null=False,verbose_name="Tema")

    def __unicode__(self):
        return '%s' % (self.description)

    class Meta:
        verbose_name = "Tema evento"
        verbose_name_plural = "Temi evento"

class Channel(models.Model):
    description = models.CharField(max_length=250,blank=False, null=False,verbose_name="Canale")

    def __unicode__(self):
        return '%s' % (self.description)

    class Meta:
        verbose_name = "Canale"
        verbose_name_plural = "Canali"

class Goal(models.Model):
    description = models.CharField(max_length=250,blank=False, null=False,verbose_name="Obiettivo")

    def __unicode__(self):
        return '%s' % (self.description)

    class Meta:
        verbose_name = "Obiettivo evento"
        verbose_name_plural = "Obiettivi evento"

class PointOfSaleType(models.Model):
    description = models.CharField(max_length=250,blank=False, null=False,verbose_name="Tipologia")

    def __unicode__(self):
        return '%s' % (self.description)

    class Meta:
        verbose_name = "Tipologia Punto Vendita"
        verbose_name_plural = "Tipologia Punto Vendita"

#TODO TO prune because not used any longer
class EventCoupon(models.Model):
    event = models.ForeignKey('campaigns.Event',blank=False,null=False,verbose_name="Evento")
    coupon = models.CharField(max_length=14,blank=False, null=False,verbose_name="Omaggio")
    used = models.BooleanField(verbose_name="Consumato",default=False)

    def __unicode__(self):
        return '(%s) %s',(self.event, self.coupon)

    class Meta:
        verbose_name = "Omaggio Evento"
        verbose_name_plural = "Omaggi Evento"

class EventType(models.Model):

    description = models.CharField(max_length=250,blank=False, null=False,verbose_name="Tipo Evento")
    contact_to_customer = models.FloatField(blank=False, verbose_name="Contatti Lordi")
    customer_to_sale = models.FloatField(blank=False, verbose_name="Contatti Netti")
    selectable = models.BooleanField(blank=False, default=True, verbose_name="Selezionabile")

    @property
    def customer_to_sale_percent(self):
        # This was created to facilitate display of percentage in the template
        return self.customer_to_sale * 100

    def __unicode__(self):
        return '%s' % (self.description)
    class Meta:
        verbose_name = "Tipo Evento"
        verbose_name_plural = "Tipi Evento"


class Event(models.Model):
    date = models.DateField(blank=False,null=False,verbose_name="Data")
    enddate = models.DateField(blank=True,null=True,verbose_name="Data di fine")
    title = models.CharField(max_length=250,blank=True,null=True, verbose_name="Titolo")
    place = models.CharField(max_length=250,blank=True,null=True, verbose_name="Indirizzo")
    province = models.ForeignKey('contacts.Province',blank=True,null=True,verbose_name="Provincia")
    description = models.CharField(max_length=500,blank=True,null=True,verbose_name="Descrizione")
    money = models.CharField(max_length=250,blank=True,null=True,verbose_name="Quota di Iscrizione")
    money_description = models.CharField(max_length=500,blank=True,null=True,verbose_name="Termini di iscrizione")
    payment = models.CharField(max_length=500,blank=True,null=True,verbose_name="Modalita\' di pagamento")
    campaign = models.ForeignKey('campaigns.Campaign',blank=True,null=True,verbose_name="Campagna relativa")
    emailcontent = RedactorField(verbose_name="Contenuto",blank=True,null=True)
    emailattachment = models.FileField(verbose_name="Allegato",blank=True,null=True,upload_to="emailattachments")
    is_public = models.BooleanField(verbose_name="Iscrizioni Aperte",blank=True,default=False)
    salestartdate = models.DateField(blank=True,null=True,verbose_name="Periodo inizio sconto")
    saleenddate = models.DateField(blank=True,null=True,verbose_name="Periodo fine sconto")
    salevalue = models.CharField(max_length=250,blank=True,null=True,verbose_name="Quota di Iscrizione Scontata")
    areamanager = models.ForeignKey('campaigns.AreaManager',blank=True,null=True,
                                    verbose_name="Area Manager",on_delete=models.SET_NULL)

    #ToDo: [REF-AREAITS] Drop AreaITS model; Drop Event.districtmanager FK as it is replaced by Event.its_districtmanager
    districtmanager = models.ForeignKey('campaigns.AreaIts', blank=True, null=True,
                                        verbose_name="District ITS Manager", on_delete=models.SET_NULL)
    its_districtmanager = models.ForeignKey(User, blank=True, null=True,
                                            verbose_name="District ITS Manager", on_delete=models.SET_NULL,
                                            related_name='my_its_events')
    #TODO to plan a task for populate its_districtmanager
    # (see setup/tasks/domenico_migrations.md document)

    owner = models.ForeignKey(User, blank=True, null=True, verbose_name="Creator of the event",
                              on_delete=models.SET_NULL, related_name='my_owned_events')

    visible_for_its = models.BooleanField(verbose_name="Pubblica evento sulle agende ITS", blank=False, default=True)

    pointofsale = models.CharField(max_length=6,blank=True,null=True,verbose_name="Codice Punto Vendita")
    pointofsaledescription = models.CharField(max_length=250,blank=True,null=True,verbose_name="Nominativo Punto Vendita")
    typepointofsale = models.ForeignKey('campaigns.PointOfSaleType',blank=True,null=True,verbose_name="Tipologia Punto Vendita",on_delete=models.SET_NULL)
    channel = models.ForeignKey('campaigns.Channel',blank=True,null=True,verbose_name="Canale",on_delete=models.SET_NULL)
    eventtype = models.ForeignKey('campaigns.EventType',blank=True,null=True,verbose_name="Tipologia Evento",on_delete=models.SET_NULL)
    theme = models.ForeignKey('campaigns.Theme',blank=True,null=True,verbose_name="Tema Evento",on_delete=models.SET_NULL)

    #TODO drop this field  - will be replaced by consultant (after population of consultant)
    trainer = models.CharField(max_length=250,blank=True, null=True, verbose_name="Relatore")
    #TODO to plan a task for populate consultant
    consultant = models.ForeignKey('contacts.Contact', blank=True, null=True, verbose_name="Relatore")

    feedback = models.SmallIntegerField(blank=True,null=True,verbose_name="Valutazione Evento")
    feedback_note = models.CharField(max_length=500,blank=True,null=True,verbose_name="Feedback Evento")
    population = models.IntegerField(blank=True,null=True,verbose_name="Numero di partecipanti")
    signups_enabled = models.BooleanField(verbose_name="Iscrizioni permesse lato frontend",blank=True,default=False)

    def __unicode__(self):
        return '%s' % (self.date.strftime("%d-%m-%Y"))

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventi'

    @property
    def is_its(self):
        if not self.owner:
            return False
        return is_its_util(self.owner) and not self.is_public

    @property
    def is_consultant_led(self):
        return self.consultant is not None


class EventSignup(models.Model):
    event = models.ForeignKey('campaigns.Event',blank=False, null=False,verbose_name="Evento")
    contact = models.ForeignKey('contacts.Contact',blank=False, null=False,verbose_name="Contatto")
    relatore = models.BooleanField(verbose_name="Relatore", default=False)
    relatore_payment = models.CharField(verbose_name="Costo relatore", max_length=100, blank=True,null=True)
    staff = models.BooleanField(verbose_name="Staff", default=False)
    omaggio = models.BooleanField(verbose_name="Omaggio", default=False)
    pagante = models.BooleanField(verbose_name="Pagante", default=False)
    note = models.CharField(verbose_name="Note",max_length=250, blank=True, null=True)
    presence = models.BooleanField(verbose_name="Presente", default=False)
    coupon = models.ForeignKey('coupon.Coupon', null=True)

    def __unicode__(self):
        return '%s %s' % (self.event, self.contact)

    class Meta:
        verbose_name = "Iscrizione evento"
        verbose_name_plural = "Iscrizioni eventi"


class EventPayment(models.Model):
    type = models.CharField(max_length=20,blank=True,null=True,verbose_name="Pagamento")
    way = models.CharField(max_length=30,blank=True,null=True,verbose_name="Modalita\'")
    note = models.CharField(blank=True,null=True,max_length=250,verbose_name="Note")
    executor = models.CharField(max_length=100,blank=True,null=True,verbose_name="Esecutore")
    street = models.CharField(max_length=100, blank=False, null=True, verbose_name='Via')
    zip = models.CharField(max_length=6, blank=False, null=True, verbose_name='CAP')
    city = models.CharField(max_length=100, blank=False, null=True, verbose_name='Comune')
    province = models.ForeignKey('contacts.Province', blank=False, null=True)
    code = models.CharField(max_length=16, blank=False, null=False,
                            verbose_name='Codice Fiscale')
    vat = models.CharField(max_length=16, blank=False, null=False, verbose_name='P.Iva')
    contact = models.ForeignKey('contacts.Contact',blank=False,null=True)
    event = models.ForeignKey('campaigns.Event',blank=False,null=True)

    def __unicode__(self):
        return '%s %s per evento %s' % (self.executor, self.way, self.event.date.strftime("%d-%m-%Y"))

    class Meta:
        verbose_name = "Pagamento iscrizione"
        verbose_name_plural = "Pagamenti iscrizioni"


class Campaign(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False, verbose_name='Nome',error_messages={'unique':"Nome gia' presente in anagrafica"})
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrizione')
    startdate = models.DateField(verbose_name='Data di inizio',error_messages={'required':"Inserire data di inizio"})
    enddate = models.DateField(verbose_name='Data di fine',error_messages={'required':"Inserire data di fine"})
    status = models.CharField(max_length=1, choices=CAMPAIGN_STATUS, default='N', verbose_name='Stato')


    def __unicode__(self):
        return '%s dal %s al %s' % (self.name,self.startdate.strftime("%d-%m-%Y"),self.enddate.strftime("%d-%m-%Y"))

    class Meta:
        verbose_name = "Campagna"
        verbose_name_plural = "Campagne"


class ProductGroup(models.Model):
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrizione')
    sell_in_alloc = models.FloatField(blank=False, verbose_name='Percentuale sell in')
    sell_in_amount = models.FloatField(blank=False, verbose_name='Valore sell in')

    @property
    def sell_in_alloc_percent(self):
        return self.sell_in_alloc * 100

    class Meta:
        verbose_name = "Gruppo di prodotto"
        verbose_name_plural = "Gruppi di prodotti"


# ###########################
# Estabilish the Relationship between
# District > ITS > Consultant
# ###########################

class District(models.Model):
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Distretto')
    district_manager = models.ForeignKey(User, null=True)

    def district_manager_displayname(self):
        dm = self.district_manager
        if dm:
            if dm.email:
                return "%s %s (%s)" % (dm.first_name, dm.last_name, dm.email)
            else:
                return "%s %s" % (dm.first_name, dm.last_name)
        else:
            return None

class ITSRelDistrict(models.Model):
    its = models.ForeignKey(User, primary_key=True)
    district = models.ForeignKey(District)


class ITSRelConsultant(models.Model):
    consultant = models.ForeignKey(Contact)
    its = models.ForeignKey(User)
