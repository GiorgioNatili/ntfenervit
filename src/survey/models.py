from __future__ import absolute_import

import datetime
import logging
from math import sin, cos
from operator import itemgetter
from textwrap import fill

import re
from survey import settings as local_settings


try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models, connection
from django.db.models import Count
from django.db.models.fields.files import ImageFieldFile
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from survey.fields import ImageWithThumbnailsField
from survey.geo import get_latitude_and_longitude
from survey.util import ChoiceEnum

from contacts.models import Contact

try:
    from positions.fields import PositionField
except ImportError:
    logging.warn('positions not installed. '
                 'Will just use integers for position fields.')
    PositionField = None

try:
    from .survey.flickrsupport import sync_to_flickr, get_group_id
except ImportError:
    logging.warn('no flickr support available')
    sync_to_flickr = None

ARCHIVE_POLICY_CHOICES = ChoiceEnum(('immediate',
                                     'post-close',
                                     'never'))

OPTION_TYPE_CHOICES = ChoiceEnum(sorted([('choice', 'Scelte esclusive'),
                                         ('char', 'Casella di testo'),
                                         ('email', 'Email'),
                                         ('integer', 'Numero Intero'),
                                         ('float', 'Numero decimale'),
                                         ('bool', 'Checkbox'),
                                         ('text', 'Area di testo'),
                                         ('select', 'Lista di scelte'),
                                         ('bool_list', 'Scelte multiple'),
                                         ('numeric_select',
                                          'Scelta numerica'),
                                         ('numeric_choice',
                                          'Lista scelte esclusive')],
                                        key=itemgetter(1)))


class LiveSurveyManager(models.Manager):
    def get_query_set(self):
        now = timezone.now()  # datetime.datetime.now()
        return super(LiveSurveyManager, self).get_query_set().filter(
            is_published=True,
            starts_at__lte=now).filter(~models.Q(archive_policy__exact=ARCHIVE_POLICY_CHOICES.NEVER) |
            models.Q(ends_at__isnull=True) |
            models.Q(ends_at__gt=now))

FORMAT_CHOICES = ('json', 'csv', 'xml', 'html',)


class Survey(models.Model):
    title = models.CharField(max_length=80, verbose_name="Titolo")
    slug = models.SlugField(unique=True, verbose_name="Slug", help_text="Campo automatico, non modificare")
    tease = models.TextField(blank=True, verbose_name="Descrizione breve")
    description = models.TextField(blank=True, verbose_name="Descrizione")
    thanks = models.TextField(
        blank=True,
        help_text="Messaggio visualizzato quando un utente invia il questionario", verbose_name="Ringraziamento finale")

    newsletter = models.ForeignKey('campaigns.Newsletter', verbose_name="Newsletter collegata", blank=True, null=True,
                                   related_name='survey_newsletter')
    event = models.ForeignKey('campaigns.Event', verbose_name="Evento collegato", blank=True, null=True,
                              related_name='survey_event')

    require_login = models.BooleanField(default=False, verbose_name="Richiede il login?")
    allow_multiple_submissions = models.BooleanField(default=False, verbose_name="Puo\' essere rifatto?")
    moderate_submissions = models.BooleanField(
        default=local_settings.MODERATE_SUBMISSIONS,
        help_text=_(u"Se selezionata, tutte le richieste saranno  NON pubbliche e "
                    "si dovra\' manualmente renderle pubbliche. "
                    "Se il sondaggio non mostra alcun risultato, e\' possibile che questa opzione sia selezionata.",
        ), verbose_name="Moderazione delle risposte?")
    allow_comments = models.BooleanField(
        default=False,
        help_text="Permetti il commento all\'invio",
        verbose_name="Permette i commenti?")
    allow_voting = models.BooleanField(
        default=False,
        help_text="Gli utenti possono votare le risposte date",
        verbose_name="Permette il voto?")
    archive_policy = models.IntegerField(
        choices=ARCHIVE_POLICY_CHOICES,
        default=ARCHIVE_POLICY_CHOICES.IMMEDIATE,
        help_text=_("Quando rendere pubbliche le risposte?"
                    "immediate: immediatamente "
                    "post-close: al termine "
                    "never: mai"),
        verbose_name="Politicha di archiviazione")
    starts_at = models.DateTimeField(default=datetime.datetime.now, verbose_name="Data di inizio")
    survey_date = models.DateField(blank=True, null=True, editable=False)
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name="Data di fine")
    is_published = models.BooleanField(default=False, verbose_name="Pubblicato")

    # email to notify at each submission
    email = models.EmailField(
        blank=True,
        help_text=("Manda email per ogni questionario compilato"))
    site = models.ForeignKey(Site)
    default_report = models.ForeignKey(
        'SurveyReport',
        blank=True,
        null=True,
        related_name='reports',
        help_text=("Link per il report"),
        verbose_name="Report collegato")

    def to_jsondata(self):
        kwargs = {'slug': self.slug}
        submit_url = reverse('embeded_survey_questions', kwargs=kwargs)
        report_url = reverse('survey_default_report_page_1', kwargs=kwargs)
        questions = self.questions.order_by("order")
        return dict(title=self.title,
                    id=self.id,
                    slug=self.slug,
                    description=self.description,
                    tease=self.tease,
                    thanks=self.thanks,
                    submit_url=submit_url,
                    report_url=report_url,
                    questions=[q.to_jsondata() for q in questions])

    def save(self, **kwargs):
        self.survey_date = self.starts_at.date()
        super(Survey, self).save(**kwargs)

    class Meta:
        ordering = ('-starts_at',)
        unique_together = (('survey_date', 'slug'),)

    @property
    def is_open(self):
        now = timezone.now()  #datetime.datetime.now()
        if self.ends_at:
            return self.starts_at <= now < self.ends_at
        return self.starts_at <= now

    @property
    def is_live(self):
        now = timezone.now()  #datetime.datetime.now()
        return all([
            self.is_published,
            self.starts_at <= now,
            any([self.archive_policy != ARCHIVE_POLICY_CHOICES.NEVER,
                 not self.ends_at or now < self.ends_at])])

    def get_public_fields(self, fieldnames=None):
        if fieldnames:
            return self.get_fields(fieldnames)
        return [f for f in self.get_fields() if f.answer_is_public]

    def get_fields(self, fieldnames=None):
        if not "_fields" in self.__dict__:
            questions = self.questions.all()
            questions = questions.select_related("survey")
            self.__dict__["_fields"] = list(questions.order_by("order"))
        fields = self.__dict__["_fields"]
        if fieldnames:
            return [f for f in fields if f.fieldname in fieldnames]
        return fields

    def get_public_archive_fields(self):
        types = (
            OPTION_TYPE_CHOICES.CHAR,
            OPTION_TYPE_CHOICES.TEXT)
        return [f for f in self.get_public_fields() if f.option_type in types]

    def icon_questions(self):
        OTC = OPTION_TYPE_CHOICES
        return self.questions.filter(
            ~models.Q(map_icons=""),
            option_type__in=[OTC.SELECT,
                             OTC.CHOICE,
                             OTC.NUMERIC_SELECT,
                             OTC.NUMERIC_CHOICE])

    def parsed_option_icon_pairs(self):
        icon_questions = self.icon_questions()
        if icon_questions:
            return icon_questions[0].parsed_option_icon_pairs()
        return ()

    def submissions_for(self, user, session_key):
        q = models.Q(survey=self)
        if user.is_authenticated():
            q = q & models.Q(user=user)
        elif session_key:
            q = q & models.Q(session_key=session_key)
        else:
            # can't pinpoint user, return none
            return Submission.objects.none()
        return Submission.objects.filter(q)

    def can_have_public_submissions(self):
        return self.archive_policy != ARCHIVE_POLICY_CHOICES.NEVER and (
            self.archive_policy == ARCHIVE_POLICY_CHOICES.IMMEDIATE or
            not self.is_open)

    def public_submissions(self):
        if not self.can_have_public_submissions():
            return self.submission_set.none()
        return self.submission_set.filter(is_public=True)

    def featured_submissions(self):
        return self.public_submissions().filter(featured=True)

    def get_filters(self):
        return self.questions.filter(use_as_filter=True,
                                     answer_is_public=True,
                                     option_type__in=FILTERABLE_OPTION_TYPES)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('survey_detail', (), {'slug': self.slug})

    def get_download_url(self, format):
        url = reverse('submissions_by_format', kwargs={"format": format})
        return url + "?survey=" + self.slug

    def get_download_tag(self, format):
        a = '<a target="_blank" href="%s">%s</a>'
        return a % (self.get_download_url(format), format,)

    def get_download_tags(self, delimiter=", "):
        downloads = []
        for format in sorted(FORMAT_CHOICES):
            downloads.append(self.get_download_tag(format))
        return delimiter.join(downloads)

    objects = models.Manager()
    live = LiveSurveyManager()

    class Meta:
        verbose_name = "Questionario"
        verbose_name_plural = "Questionari"


FILTERABLE_OPTION_TYPES = (OPTION_TYPE_CHOICES.INTEGER,
                           OPTION_TYPE_CHOICES.FLOAT,
                           OPTION_TYPE_CHOICES.BOOL,
                           OPTION_TYPE_CHOICES.SELECT,
                           OPTION_TYPE_CHOICES.CHOICE,
                           OPTION_TYPE_CHOICES.NUMERIC_SELECT,
                           OPTION_TYPE_CHOICES.NUMERIC_CHOICE)

POSITION_HELP = ("Posizione nel questionario")


class Question(models.Model):
    survey = models.ForeignKey(Survey, related_name="questions")
    fieldname = models.CharField(
        max_length=32,
        help_text=_('identificativo della domanda senza spazi ne trattini es. domanda_1'),
        verbose_name="Identificativo unico"
    )
    question = models.TextField(help_text=_(
        "Testo che compare all'utente"), verbose_name="Testo della domanda")
    label = models.TextField(help_text=_("Nome che compare nel report"))
    help_text = models.TextField(
        blank=True, verbose_name="Descrizione di aiuto per l'utente")
    required = models.BooleanField(
        default=False,
        verbose_name=_("Domanda obbligatoria?"))
    if PositionField:
        order = PositionField(
            collection=('survey',),
            help_text=_(POSITION_HELP + " Use -1 to auto-assign."))
    else:
        order = models.IntegerField(help_text=POSITION_HELP, verbose_name="Ordine")
    option_type = models.CharField(
        max_length=max([len(key) for key, v in OPTION_TYPE_CHOICES._choices]),
        choices=OPTION_TYPE_CHOICES,
        help_text=_('In un questionario attivo non modificare questa opzione'),
        verbose_name="Tipologia risposta")
    # For NUMERIC_(SELECT|CHOICE) use it as an int unless they use a decimal. 
    numeric_is_int = models.BooleanField(default=True, editable=False)
    options = models.TextField(
        blank=True,
        default='',
        help_text=_(
            'Usa una risposta per riga'), verbose_name="Risposte possibili")
    correct_answer = models.CharField(verbose_name="Risposta Corretta", blank=True, null=True, max_length=100)
    score = models.IntegerField(verbose_name="Punteggio risposta", blank=True, null=True)
    answer_is_public = models.BooleanField(default=True, verbose_name="Risposta pubblica")
    use_as_filter = models.BooleanField(default=True, verbose_name="Usa come filtro")
    _aggregate_result = None

    @property
    def is_filterable(self):
        return (self.use_as_filter and
                self.option_type in FILTERABLE_OPTION_TYPES)

    def to_jsondata(self):
        return dict(fieldname=self.fieldname,
                    label=self.label,
                    is_filterable=self.is_filterable,
                    question=self.question,
                    required=self.required,
                    option_type=self.option_type,
                    options=self.parsed_options,
                    answer_is_public=self.answer_is_public,
                    cms_id=self.id,
                    help_text=self.help_text)

    @property
    def public_answers(self):
        if self.answer_is_public:
            return self.answer_set.filter(submission__is_public=True)
        return self.answer_set.none()

    class Meta:
        ordering = ('order',)
        unique_together = ('fieldname', 'survey')

    def __unicode__(self):
        return self.question

    def save(self, *args, **kwargs):
        self.numeric_is_int = True
        OTC = OPTION_TYPE_CHOICES
        if self.option_type in (OTC.NUMERIC_SELECT, OTC.NUMERIC_CHOICE):
            for option in self.parsed_options:
                try:
                    int(option)
                except ValueError:
                    float(option)
                    self.numeric_is_int = False
        elif self.option_type == OTC.FLOAT:
            self.numeric_is_int = False
        super(Question, self).save(*args, **kwargs)

    @property
    def parsed_options(self):
        if OPTION_TYPE_CHOICES.BOOL == self.option_type:
            return [True, False]
        return filter(None, (s.strip() for s in self.options.splitlines()))

    @property
    def parsed_map_icons(self):
        return filter(None, (s.strip() for s in self.map_icons.splitlines()))

    def parsed_option_icon_pairs(self):
        options = self.parsed_options
        icons = self.parsed_map_icons
        to_return = []
        for i in range(len(options)):
            if i < len(icons):
                to_return.append((options[i], icons[i]))
            else:
                to_return.append((options[i], None))
        return to_return

    @property
    def value_column(self):
        ot = self.option_type
        OTC = OPTION_TYPE_CHOICES
        if ot == OTC.BOOL:
            return "boolean_answer"
        elif self.is_float:
            return "float_answer"
        elif self.is_integer:
            return "integer_answer"
        return "text_answer"

    @property
    def is_numeric(self):
        OTC = OPTION_TYPE_CHOICES
        return self.option_type in [OTC.FLOAT,
                                    OTC.INTEGER,
                                    OTC.BOOL,
                                    OTC.NUMERIC_SELECT,
                                    OTC.NUMERIC_CHOICE]

    @property
    def is_float(self):
        return self.is_numeric and not self.numeric_is_int

    @property
    def is_integer(self):
        return self.is_numeric and self.numeric_is_int

    class Meta:
        verbose_name = "Domanda"
        verbose_name_plural = "Domande"


FILTER_TYPE = ChoiceEnum("choice range distance")


class Filter:
    def __init__(self, field, request_data):
        self.field = field
        self.key = field.fieldname
        self.label = field.label
        self.choices = field.parsed_options
        self.value = self.from_value = self.to_value = ""
        self.within_value = self.location_value = ""

        def get_val(suffix):
            return request_data.get(self.key + suffix, "").replace("+", " ")

        if field.option_type in (OPTION_TYPE_CHOICES.BOOL,
                                 OPTION_TYPE_CHOICES.CHOICE,
                                 OPTION_TYPE_CHOICES.SELECT,
                                 OPTION_TYPE_CHOICES.NUMERIC_CHOICE,
                                 OPTION_TYPE_CHOICES.NUMERIC_SELECT):
            self.type = FILTER_TYPE.CHOICE
            self.value = get_val("")
        elif field.option_type in (OPTION_TYPE_CHOICES.INTEGER,
                                   OPTION_TYPE_CHOICES.FLOAT):
            self.type = FILTER_TYPE.RANGE
            self.from_value = get_val("_from")
            self.to_value = get_val("_to")


def get_filters(survey, request_data):
    fields = list(survey.get_public_fields())
    return [Filter(f, request_data) for f in fields if f.is_filterable]


def extra_from_filters(set, submission_id_column, survey, request_data):
    sid = submission_id_column
    for where, params in extra_clauses_from_filters(sid, survey, request_data):
        set = set.extra(where=[where], params=params)
    return set


def extra_clauses_from_filters(submission_id_column, survey, request_data):
    return_value = []
    for filter in get_filters(survey, request_data):
        loc = filter.location_value and filter.within_value
        if filter.value or filter.from_value or filter.to_value or loc:
            try:
                OTC = OPTION_TYPE_CHOICES
                where = "".join((
                    submission_id_column,
                    " IN (SELECT submission_id FROM ",
                    "survey_answer WHERE question_id = %d ",
                    "AND ")) % filter.field.id
                if OTC.BOOL == filter.field.option_type:
                    f = ("0", "f",)
                    length = len(filter.value)
                    params = [length and not filter.value[0].lower() in f]
                    where += "boolean_answer = %s"
                elif filter.field.is_numeric:
                    column = filter.field.value_column
                    convert = float if filter.field.is_float else int
                    params = []
                    wheres = []
                    if filter.from_value:
                        params.append(convert(filter.from_value))
                        wheres.append("%s <= " + column)
                    if filter.to_value:
                        params.append(convert(filter.to_value))
                        wheres.append(column + " <= %s")
                    if filter.value:
                        params.append(convert(filter.value))
                        wheres.append(column + " = %s")
                    where += " AND ".join(wheres)
                else:
                    params = [filter.value]
                    where += "text_answer = %s"
                where += ")"
                return_value.append((where, params,))
            except ValueError:
                pass
    return return_value


def _extra_from_distance(filter, submission_id_column):
    """ This uses the Spherical Law of Cosines for a close enough approximation
    of distances. distance = acos(sin(lat1) * sin(lat2) +
                                  cos(lat1) * cos(lat2) *
                                  cos(lng2 - lng1)) * 3959
    The "radius" of the earth varies between 3,950 and 3,963 miles. """
    spaces = re.compile(r'\s')
    key = spaces.sub("+", "lat_lng_of_" + str(filter.location_value.lower()))
    lat_lng = cache.get(key, None)
    if lat_lng is None:
        lat_lng = get_latitude_and_longitude(filter.location_value)
        cache.set(key, lat_lng)
    (lat, lng) = lat_lng
    if lat is None or lng is None:
        return
    acos_of_args = (
        sin(_radians(lat)),
        _D_TO_R,
        cos(_radians(lat)),
        _D_TO_R,
        lng,
        _D_TO_R)
    acos_of = (
                  "%f * sin(latitude / %f) + "
                  "%f * cos(latitude / %f) * "
                  "cos((longitude - %f) / %f)") % acos_of_args
    # if acos_of >= 1 then the address in the database is practically the
    # same address we're searching for and acos(acos_of) is mathematically 
    # impossible so just always include it. If acos_of < 1 then we need to
    # check the distance.
    where = "".join((
        submission_id_column,
        " IN (SELECT ca.submission_id FROM ",
        "survey_answer AS ca JOIN survey_submission AS cs ",
        "ON ca.submission_id = cs.id ",
        "WHERE cs.survey_id = %s AND latitude IS NOT NULL ",
        "AND longitude IS NOT NULL AND ",
        acos_of,
        " >= 1 OR (",
        acos_of,
        " < 1 AND 3959.0 * acos(",
        acos_of,
        ") <= %s))"))
    params = [int(filter.field.survey_id), int(filter.within_value)]
    return where, params


_D_TO_R = 57.295779


def _radians(degrees):
    return degrees / _D_TO_R


class AggregateResultCount(object):
    """ This helper class makes it easier to write templates that display
    pie charts. """

    def __init__(self,
                 survey,
                 field,
                 request_data,
                 surveyreport=None,
                 is_staff=False):
        self.answer_set = field.answer_set.none()
        self.answer_value_lookup = {}
        if is_staff or field.answer_is_public:
            self.answer_set = field.public_answers
            if is_staff:
                self.answer_set = field.answer_set
            self.answer_set = self.answer_set.values(field.value_column)
            self.answer_set = self.answer_set.annotate(count=Count("id"))
            self.answer_set = extra_from_filters(self.answer_set,
                                                 "submission_id",
                                                 survey,
                                                 request_data)
            if surveyreport and surveyreport.featured:
                self.answer_set = self.answer_set.filter(
                    submission__featured=True)
        for answer in self.answer_set:
            text = fill(u"%s" % answer[field.value_column], 30)
            if answer["count"]:
                self.answer_value_lookup[text] = {
                    field.fieldname: text,
                    "count": answer["count"]}
        # 2-axis aggregate results put the results in the same order as the
        # options, so we do that here as well to make 1-axis graphs like pie
        # charts and simple count bar charts match.
        self.answer_values = []
        for answer in field.parsed_options:
            value = self.answer_value_lookup.pop(answer, None)
            if value:
                self.answer_values.append(value)
        for value in self.answer_value_lookup.values():
            self.answer_values.append(value)
        self.yahoo_answer_string = json.dumps(self.answer_values)


class AggregateResult2Axis(object):
    def __init__(
            self,
            y_axes,
            x_axis,
            request_data,
            aggregate_function,
            report):
        self.answer_values = []
        answer_value_lookup = {}

        def new_answer_value(x_value):
            answer_value = {x_axis.fieldname: x_value}
            for y_axis in y_axes:
                answer_value[y_axis.fieldname] = 0
            answer_value_lookup[x_value] = answer_value
            self.answer_values.append(answer_value)
            return answer_value

        # We could just add new x-axis values as we encounter them. However,
        # say someone has parsed_options ["January", ... , "December"].
        # Then doing it this way puts them in order.
        [new_answer_value(x_value) for x_value in x_axis.parsed_options]

        x_value_column = "x_axis." + x_axis.value_column
        for y_axis in y_axes:
            params = [y_axis.id, x_axis.id]
            y_axis_column = y_axis.value_column
            if "boolean_answer" == y_axis_column:
                y_axis_column = "CAST(y_axis." + y_axis_column + " AS int)"
            else:
                y_axis_column = "y_axis." + y_axis_column
            query = [
                "SELECT ",
                x_value_column,
                " AS x_value, ",
                aggregate_function,
                "(",
                y_axis_column,
                ") AS y_value FROM survey_answer AS y_axis ",
                "JOIN survey_answer AS x_axis "
                "ON y_axis.submission_id = x_axis.submission_id ",
                "JOIN survey_submission AS submission ",
                "ON submission.id = y_axis.submission_id ",
                "WHERE submission.is_public = true AND ",
                "y_axis.question_id = %s AND ",
                y_axis_column,
                " IS NOT NULL AND x_axis.question_id = %s"]
            if report and report.featured:
                query.append(" AND submission.featured = true")
            y = "y_axis.submission_id"
            extras = extra_clauses_from_filters(y, x_axis.survey, request_data)
            for where, next_params in extras:
                query.append(" AND ")
                query.append(where)
                params += next_params
            query.append(" GROUP BY ")
            query.append(x_value_column)
            cursor = connection.cursor()
            cursor.execute("".join(query), params)
            found_any = False
            for x_value, y_value in cursor.fetchall():
                found_any = True
                if isinstance(y_value, Decimal):
                    y_value = round(y_value, 2)
                answer_value = answer_value_lookup.get(x_value)
                if not answer_value:
                    answer_value = new_answer_value(x_value)
                answer_value[y_axis.fieldname] += y_value
        if x_axis.is_numeric:
            key = x_axis.fieldname
            self.answer_values.sort(lambda x, y: x[key] - y[key])
        if not found_any:
            self.answer_values = []
        self.yahoo_answer_string = json.dumps(self.answer_values)


class AggregateResultSum(AggregateResult2Axis):
    def __init__(self, y_axes, x_axis, request_data, report=None):
        sup = super(AggregateResultSum, self)
        sup.__init__(y_axes, x_axis, request_data, "SUM", report)


class AggregateResultAverage(AggregateResult2Axis):
    def __init__(self, y_axes, x_axis, request_data, report=None):
        sup = super(AggregateResultAverage, self)
        sup.__init__(y_axes, x_axis, request_data, "AVG", report)


class AggregateResult2AxisCount(AggregateResult2Axis):
    def __init__(self, y_axes, x_axis, request_data, report=None):
        sup = super(AggregateResult2AxisCount, self)
        sup.__init__(y_axes, x_axis, request_data, "COUNT", report)


BALLOT_STUFFING_FIELDS = ('ip_address', 'session_key',)


class Submission(models.Model):
    OPENED = 0
    COMPLETED = 1
    STATUS_CHOICES = ((OPENED, 'Opened'), (COMPLETED, 'Completed'),)

    survey = models.ForeignKey(Survey)
    contact = models.ForeignKey(Contact, blank=True, null=True)
    ip_address = models.IPAddressField()
    submitted_at = models.DateTimeField(default=datetime.datetime.now, editable=False)
    session_key = models.CharField(max_length=40, blank=True, editable=False)
    featured = models.BooleanField(default=False)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=COMPLETED, blank=True, null=True, editable=False)
    # for moderation
    is_public = models.BooleanField(
        default=True,
        help_text=_("Crowdsourcing only displays public submissions. The "
                    "'Moderate submissions' checkbox of the survey determines "
                    "the default value of this field."))

    # class Meta:


    def to_jsondata(self, answer_lookup=None, include_private_questions=False):
        def to_json(v):
            if isinstance(v, ImageFieldFile):
                return v.url if v else ''
            return v

        if not answer_lookup:
            answer_lookup = get_all_answers([self], include_private_questions)
        data = {}
        for a in answer_lookup.get(self.pk, []):
            if a.question.option_type == OPTION_TYPE_CHOICES.BOOL_LIST:
                data[a.value] = True
            else:
                data[a.question.fieldname] = to_json(a.value)
        return_value = dict(data=data,
                            survey=self.survey.slug,
                            submitted_at=self.submitted_at,
                            featured=self.featured,
                            is_public=self.is_public)
        if include_private_questions:
            for key in BALLOT_STUFFING_FIELDS:
                return_value[key] = getattr(self, key)
        if self.contact:
            return_value["contact"] = self.contact.email
        return return_value

    def get_answer_dict(self):
        try:
            # avoid called __getattr__
            return self.__dict__['_answer_dict']
        except KeyError:
            answers = self.answer_set.all()
            d = dict((a.question.fieldname, a.value) for a in answers)
            self.__dict__['_answer_dict'] = d
            return d

    def items(self):
        return self.get_answer_dict().items()

    def get_absolute_url(self):
        view = 'survey.views.submission'
        return reverse(view, kwargs={"id": self.pk})

    @property
    def email(self):
        return self.get_answer_dict().get('email', '')

    def __unicode__(self):
        return u"%s Submission" % self.survey.title

    def save(self, *args, **kwargs):
        self.submitted_at = datetime.datetime.now()
        print 'saving submission! '+str(self.status)
        return super(Submission, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Compilazione"
        verbose_name_plural = "Compilazioni"
        ordering = ('-submitted_at',)


class Answer(models.Model):
    class Meta:
        ordering = ('question',)
        verbose_name = "Risposta"
        verbose_name_plural = "Risposte"

    submission = models.ForeignKey(Submission)
    question = models.ForeignKey(Question)
    text_answer = models.TextField(blank=True)
    integer_answer = models.IntegerField(blank=True, null=True)
    float_answer = models.FloatField(blank=True, null=True)
    boolean_answer = models.NullBooleanField()
    image_answer_thumbnail_meta = dict(size=(250, 250))  # width, height
    image_answer = ImageWithThumbnailsField(
        max_length=500,
        blank=True,
        thumbnail=image_answer_thumbnail_meta,
        extra_thumbnails=local_settings.EXTRA_THUMBNAILS,
        upload_to=local_settings.IMAGE_UPLOAD_PATTERN)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    flickr_id = models.CharField(max_length=64, blank=True)
    photo_hash = models.CharField(max_length=40,
                                  null=True,
                                  blank=True,
                                  editable=False)

    # def value():

    def get(self):
        return getattr(self, self.question.value_column)

    def set(self, v):
        ot = self.question.option_type
        OTC = OPTION_TYPE_CHOICES
        if ot == OTC.BOOL:
            self.boolean_answer = bool(v)
        elif ot in (OTC.FLOAT,
                    OTC.INTEGER,
                    OTC.NUMERIC_SELECT,
                    OTC.NUMERIC_CHOICE):
            # Keep values in both the integer and float columns just in
            # case the question switches between integer and float types.
            if v:
                self.float_answer = float(v)
                self.integer_answer = int(round(self.float_answer))
            else:
                self.float_answer = self.integer_answer = None
        else:
            self.text_answer = v

        # return get, set

    value = property(get, set)

    def save(self, **kwargs):
        # or should this be in a signal?  Or build in an option
        # to manage asynchronously? @TBD
        if local_settings.SYNCHRONOUS_FLICKR_UPLOAD:
            self._sync_self_to_flickr()
        super(Answer, self).save(**kwargs)

    def __unicode__(self):
        return unicode(self.question)

    def _sync_self_to_flickr(self):
        """ Does not save. You must save after syncing. """
        if sync_to_flickr:
            survey = self.question.survey
            if survey.flickr_group_id:
                try:
                    sync_to_flickr(self, survey.flickr_group_id)
                except Exception as ex:
                    message = "error in syncing to flickr: %s" % str(ex)
                    logging.exception(message)

    @classmethod
    def sync_to_flickr(cls):
        if sync_to_flickr:
            answers = cls.objects.filter(
                image_answer__gt='',
                flickr_id='',
                question__survey__flickr_group_id__gt='')
            answers = answers.select_related("question__survey")
            for answer in answers:
                answer._sync_self_to_flickr()
                answer.save()


class SurveyReport(models.Model):
    """
    a survey report permits the presentation of data submitted in a
    survey to be customized.  It consists of a series of display
    options, which each take a display type, a series of fieldnames,
    and an annotation.  It also has article-like fields of its own.
    """
    survey = models.ForeignKey(Survey)
    title = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("You may leave this field blank. Crowdsourcing will use "
                    "the survey title as a default."))
    slug = models.CharField(
        max_length=50,
        help_text=_("The default is the description of the survey."))
    # some text at the beginning
    summary = models.TextField(blank=True)
    # As crowdsourcing doesn't implement rating because we want to let you use
    # your own, we don't actually use this flag anywhere in the crowdsourcing
    # project. Rather, see settings.PRE_REPORT
    sort_by_rating = models.BooleanField(
        default=False,
        help_text="By default, sort descending by highest rating. Otherwise, "
                  "the default sort is by date descending.")
    display_the_filters = models.BooleanField(
        default=True,
        help_text="Display the filters at the top of the report page.")
    limit_results_to = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Only use the top X submissions.")
    featured = models.BooleanField(
        default=False,
        help_text=_("Include only featured submissions."))
    display_individual_results = models.BooleanField(
        default=True,
        help_text=_("Display separate, individual results if this field is "
                    "True and you have archivable questions, like those with "
                    "paragraph answers."))
    # A useful variable for holding different report displays so they don't
    # get saved to the database.
    survey_report_displays = None

    def get_survey_report_displays(self):
        if self.pk and self.survey_report_displays is None:
            srds = list(self.surveyreportdisplay_set.select_related('report'))
            self.survey_report_displays = srds
            for srd in self.survey_report_displays:
                srd._report = self
        return self.survey_report_displays

    def has_display_type(self, type):
        if not hasattr(type, '__iter__'):
            type = [type]
        displays = self.get_survey_report_displays()
        return bool([1 for srd in displays if srd.display_type in type])

    def has_charts(self):
        SRDC = SURVEY_DISPLAY_TYPE_CHOICES
        return self.has_display_type([SRDC.PIE, SRDC.BAR, SRDC.LINE])

    @models.permalink
    def get_absolute_url(self):
        return ('survey_report_page_1', (), {'slug': self.survey.slug,
                                             'report': self.slug})

    class Meta:
        unique_together = (('survey', 'slug'),)
        ordering = ('title',)

    def get_title(self):
        return self.title or self.survey.title

    def get_summary(self):
        return self.summary or self.survey.description or self.survey.tease

    def __unicode__(self):
        return self.get_title()

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Report"


SURVEY_DISPLAY_TYPE_CHOICES = ChoiceEnum(
    'text pie map bar line slideshow download')

SURVEY_AGGREGATE_TYPE_CHOICES = ChoiceEnum('default sum count average')


class SurveyReportDisplay(models.Model):
    """ Think of this as a line item of SurveyReport. """
    report = models.ForeignKey(SurveyReport)
    display_type = models.PositiveIntegerField(
        choices=SURVEY_DISPLAY_TYPE_CHOICES)
    aggregate_type = models.PositiveIntegerField(
        choices=SURVEY_AGGREGATE_TYPE_CHOICES,
        help_text=_("We only use this field if you chose a Bar or Line Chart. "
                    "How should we aggregate the y-axis? 'Average' is good "
                    "for things like ratings, 'Sum' is good for totals, and "
                    "'Count' is good for a show of hands."),
        default=SURVEY_AGGREGATE_TYPE_CHOICES.DEFAULT)
    fieldnames = models.TextField(
        blank=True,
        help_text=_("Pull these values from Survey -> Questions -> Fieldname. "
                    "Separate by spaces. These are the y-axes of bar and line "
                    "charts."))
    x_axis_fieldname = models.CharField(
        blank=True,
        help_text=_("This only applies to bar and line charts. Use only 1 "
                    "field."),
        max_length=80)
    annotation = models.TextField(blank=True)
    limit_map_answers = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Google maps gets pretty slow if you add too many points. '
                    'Use this field to limit the number of points that '
                    'display on the map.'))
    map_center_latitude = models.FloatField(
        blank=True,
        null=True,
        help_text=_('If you don\'t specify latitude, longitude, or zoom, the '
                    'map will just center and zoom so that the map shows all '
                    'the points.'))
    map_center_longitude = models.FloatField(blank=True, null=True)
    map_zoom = models.IntegerField(
        blank=True,
        null=True,
        help_text=_('13 is about the right level for Manhattan. 0 shows the '
                    'entire world.'))
    caption_fields = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('The answers to these questions will appear as '
                    'captions below their corresponding slides. Separate by '
                    'spaces.'))

    if PositionField:
        order = PositionField(collection=('report',))
    else:
        order = models.IntegerField()

    def __unicode__(self):
        type = SURVEY_DISPLAY_TYPE_CHOICES.getdisplay(self.display_type)
        return_value = [type]
        SATC = SURVEY_AGGREGATE_TYPE_CHOICES
        if self.aggregate_type != SATC.DEFAULT:
            return_value.append(SATC.getdisplay(self.aggregate_type))
        if self.x_axis_fieldname:
            if self.fieldnames:
                return_value.append("y-axes: %s" % self.fieldnames)
            return_value.append("x-axis: %s" % self.x_axis_fieldname)
        elif self.fieldnames:
            return_value.append(self.fieldnames)
        return " ".join(return_value)

    def questions(self, fields=None):
        return self._get_questions(self.fieldnames, fields)

    def x_axis_question(self, fields=None):
        return_value = self._get_questions(self.x_axis_fieldname, fields)
        if return_value:
            return return_value[0]
        return None

    def get_caption_fieldnames(self):
        return self.caption_fields.split(" ")

    def _get_questions(self, fieldnames, fields):
        names = fieldnames.split(" ")
        if fields:
            return [f for f in fields if f.fieldname in names]
        return self.get_report().survey.get_public_fields(names)

    def get_report(self):
        if hasattr(self, '_report'):
            return self._report
        return self.report

    def index_in_report(self):
        assert self.report, "This display's report attribute is not set."
        srds = self.get_report().get_survey_report_displays()
        for i in range(len(srds)):
            if srds[i] == self:
                return i
        assert False, "This display isn't in its report's displays."

    class Meta:
        ordering = ('order',)

    def __getattribute__(self, key):
        """ We provide is_text, is_pie, etc... as attirbutes to make it easier
        to write conditional logic in Django templates based on
        display_type. """
        if "is_" == key[:3]:
            for value, name in SURVEY_DISPLAY_TYPE_CHOICES._choices:
                if name == key[3:]:
                    return self.display_type == value
        return super(SurveyReportDisplay, self).__getattribute__(key)


def get_all_answers(submission_list, include_private_questions=False):
    ids = [submission.id for submission in submission_list]
    page_answers_list = Answer.objects.filter(submission__id__in=ids)
    if not include_private_questions:
        kwargs = dict(question__answer_is_public=True)
        page_answers_list = page_answers_list.filter(**kwargs)
    page_answers_list = page_answers_list.select_related("question")
    page_answers = {}
    for answer in page_answers_list:
        if not answer.submission_id in page_answers:
            page_answers[answer.submission_id] = []
        page_answers[answer.submission_id].append(answer)
    return page_answers
