from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
# Create your models here.

SEX_CHOICES = (
    ('m', 'Maschile'),
    ('f', 'Femminile'),
    ('n', 'Neutro'),
)

REGION_POSITION_LIST = (
    ('N', _('Nord')),
    ('C', _('Centro')),
    ('S', _('Sud')),
    ('I', _('Isole')),
)

CONTACT_STATUS = (
    ('A', 'Attivo'),
    ('N', 'Non Attivo'),
    ('I', 'Inerte'),
    ('C', 'Cancellato'),
    ('D', 'Non Interessato'),
)

CONTACT_TYPE = (('N', 'Normale'), ('C', 'Consulente'))


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False, verbose_name='Denominazione',error_messages={'unique':"Denominazione gia' presente in anagrafica"})
    vat = models.CharField(primary_key=True, max_length=20, blank=False, null=False, verbose_name='P.Iva', unique=True, error_messages={'unique':"P.Iva presente gia' in anagrafica"})
    email = models.EmailField(blank=True, null=True, verbose_name='Email', unique=True,error_messages={'unique':"Email gia' presente in anagrafica"})
    street = models.CharField(max_length=100, blank=False, null=True, verbose_name='Via')
    civic = models.CharField(max_length=5, blank=True, verbose_name='Civico',error_messages={'max_length':"Civico non valido. Massimo 5 cifre"})
    city = models.CharField(max_length=100, blank=False, null=True, verbose_name='Comune')
    province = models.ForeignKey('contacts.Province', blank=False, null=True)
    company_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='Codice Azienda')

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Azienda"
        verbose_name_plural = "Aziende"


class Region(models.Model):
    """
    Italian Regions
    References: http://it.wikipedia.org/wiki/Regioni_dell%27Italia
    Github: https://github.com/Immediatic/django-provinceitaliane
    """
    name = models.CharField(verbose_name='Name', max_length=30)
    position = models.CharField(verbose_name='Posizione', max_length=1, choices=REGION_POSITION_LIST)
    special = models.BooleanField(verbose_name='Statuto speciale', default=False)
    coat = models.URLField(verbose_name='Stemma', max_length=200, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        ordering = ['name']
        verbose_name = "Regione"
        verbose_name_plural = "Regioni"


class Province(models.Model):
    code = models.CharField(verbose_name='Sigla', max_length=2, unique=True)
    name = models.CharField(verbose_name='Nome', max_length=50)
    region = models.ForeignKey('contacts.Region', verbose_name='Regione')
    capital = models.BooleanField(verbose_name='Capoluogo', default=False)
    coat = models.URLField(verbose_name='Stemma', max_length=200, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        ordering = ['code']
        verbose_name = 'Provincia'
        verbose_name_plural = 'Province'


class Division(models.Model):
    name = models.CharField(unique=True, max_length=100, blank=False, null=False, verbose_name='Nome')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrizione')

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Divisione"
        verbose_name_plural = "Divisioni"


class SubDivision(models.Model):
    name = models.CharField(unique=True, max_length=100, blank=False, null=False, verbose_name='Nome')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrizione')
    category = models.ForeignKey('contacts.Division', verbose_name='Divisione')

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "SottoCategoria"
        verbose_name_plural = "SottoCategorie"


class Sector(models.Model):
    name = models.CharField(unique=True, max_length=100, blank=False, null=False, verbose_name='Nome')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrizione')

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Settore"
        verbose_name_plural = "Settori"


class Work(models.Model):
    name = models.CharField(unique=True, max_length=100, blank=False, null=False, verbose_name='Nome')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Descrizione')
    sector = models.ForeignKey('contacts.Sector', verbose_name='Settore')

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Professione"
        verbose_name_plural = "Professioni"


class Visit(models.Model):
    date = models.DateField(verbose_name='Data visita')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dettagli')
    contact = models.ForeignKey('contacts.Contact', verbose_name='Contatto')

    def __unicode__(self):
        return 'Visita del %s a %s' % (self.date, self.contact)

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visite"


class ChampionsDelivery(models.Model):
    date = models.DateField(verbose_name='Data ricezione')
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dettagli')
    contact = models.ForeignKey('contacts.Contact', verbose_name='Contatto')

    def __unicode__(self):
        return 'Consegna del %s a %s' % (self.date, self.contact)

    class Meta:
        verbose_name = "Consegna campioni"
        verbose_name_plural = "Consegne campioni"


class Payment(models.Model):
    date = models.DateField(verbose_name='Data pagamento')
    value = models.DecimalField(verbose_name='Importo', blank=True, null=True,max_digits=8, decimal_places=2)
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dettagli')
    contact = models.ForeignKey('contacts.Contact', verbose_name='Contatto')

    def __unicode__(self):
        return 'Pagamento del %s a %s' % (self.date, self.contact)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamenti"


class Contact(models.Model):

    type = models.CharField(max_length=1, choices=CONTACT_TYPE, default='N', verbose_name='Tipo Contatto')

    name = models.CharField(max_length=100, blank=False, null=False, verbose_name='Nome')
    surname = models.CharField(max_length=100, blank=False, null=False, verbose_name='Cognome')
    code = models.CharField(primary_key=True, max_length=16, blank=False, null=False,
                            verbose_name='Codice Fiscale', unique=True)
    email = models.EmailField(blank=True, null=True, verbose_name='Email', unique=False)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='m', verbose_name='Sesso')
    birthdate = models.DateField(verbose_name='Data di nascita',blank=True,null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True,verbose_name='Telefono')
    street = models.CharField(max_length=100, blank=False, null=True, verbose_name='Via')
    civic = models.CharField(max_length=5, blank=True, verbose_name='Civico')
    city = models.CharField(max_length=100, blank=False, null=True, verbose_name='Comune')
    zip = models.CharField(max_length=6, blank=True, null=True, verbose_name='CAP')
    province = models.ForeignKey('contacts.Province', blank=False, null=True)
    work = models.ForeignKey('contacts.Work',blank=True,null=True,verbose_name='Professione')
    company = models.ForeignKey('contacts.Company', blank=True, null=True, verbose_name='Azienda di appartenenza')
    status = models.CharField(max_length=1, choices=CONTACT_STATUS, default='I', verbose_name='Stato')
    privacy_consensus = models.BooleanField(verbose_name='Consenso della privacy',default=True)
    participation_ranking = models.IntegerField(default=0, verbose_name='Partecipazione',
                                                help_text='Ranking di partecipazione')
    company_ranking = models.IntegerField(default=0, verbose_name='Importanza',
                                          help_text='Ranking di importanza aziendale')
    anagrafic_subdivision = models.ManyToManyField('contacts.SubDivision', blank=True,
                                                   verbose_name='Preferenza di Attributo',
                                                   related_name='contact_anagrafic_subdivision')
    action_subdivision = models.ManyToManyField('contacts.SubDivision', blank=True, null=True,verbose_name='Preferenza di Azione',
                                                related_name='contact_action_subdivision')
    owner = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.name, self.surname)

    class Meta:
        verbose_name = "Contatto"
        verbose_name_plural = "Contatti"


class RankingConfiguration(models.Model):
    minvalue = models.PositiveSmallIntegerField(verbose_name="Valore minimo",blank=False,null=False,default=0)
    maxvalue = models.PositiveSmallIntegerField(verbose_name="Valore massimo",blank=False,null=False,default=10)
    eventsignup = models.PositiveSmallIntegerField(verbose_name="Premio iscrizione evento",blank=False,null=False,default=1)
    eventpresence = models.PositiveSmallIntegerField(verbose_name="Premio presenza evento",blank=False,null=False,default=1)
    survey = models.PositiveSmallIntegerField(verbose_name="Premio risposta questionario",blank=False,null=False,default=1)
    inactive = models.SmallIntegerField(verbose_name="Penalizzazione per inattivita\'",blank=False,null=False,default=-1)
    active_threshold = models.PositiveSmallIntegerField(verbose_name="Valore di soglia contatto ATTIVO",blank=False,null=False,default=1)
    inactivity_period = models.PositiveSmallIntegerField(verbose_name="Periodo di inattivita\'",blank=False,null=False,default=24)

    class Meta:
        verbose_name = "Configurazione Ranking"
        verbose_name_plural = "Configurazione Ranking"
