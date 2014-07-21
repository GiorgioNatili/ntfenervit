# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Survey'
        db.create_table(u'survey_survey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('tease', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('thanks', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('newsletter', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='survey_newsletter', null=True, to=orm['campaigns.Newsletter'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='survey_event', null=True, to=orm['campaigns.Event'])),
            ('require_login', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_multiple_submissions', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('moderate_submissions', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_comments', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_voting', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('archive_policy', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('starts_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('survey_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('ends_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('default_report', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reports', null=True, to=orm['survey.SurveyReport'])),
        ))
        db.send_create_signal(u'survey', ['Survey'])

        # Adding model 'Question'
        db.create_table(u'survey_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', to=orm['survey.Survey'])),
            ('fieldname', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('label', self.gf('django.db.models.fields.TextField')()),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('option_type', self.gf('django.db.models.fields.CharField')(max_length=14)),
            ('numeric_is_int', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('options', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('correct_answer', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('answer_is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('use_as_filter', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'survey', ['Question'])

        # Adding model 'Submission'
        db.create_table(u'survey_submission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Survey'])),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Contact'], null=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('submitted_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'survey', ['Submission'])

        # Adding model 'Answer'
        db.create_table(u'survey_answer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Submission'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'])),
            ('text_answer', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('integer_answer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('float_answer', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('boolean_answer', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('image_answer', self.gf('survey.fields.ImageWithThumbnailsField')(max_length=500, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('flickr_id', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('photo_hash', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal(u'survey', ['Answer'])

        # Adding model 'SurveyReport'
        db.create_table(u'survey_surveyreport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Survey'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('summary', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('sort_by_rating', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_the_filters', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('limit_results_to', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_individual_results', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'survey', ['SurveyReport'])

        # Adding model 'SurveyReportDisplay'
        db.create_table(u'survey_surveyreportdisplay', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyReport'])),
            ('display_type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('aggregate_type', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('fieldnames', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('x_axis_fieldname', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('annotation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('limit_map_answers', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('map_center_latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('map_center_longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('map_zoom', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('caption_fields', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal(u'survey', ['SurveyReportDisplay'])


    def backwards(self, orm):
        # Deleting model 'Survey'
        db.delete_table(u'survey_survey')

        # Deleting model 'Question'
        db.delete_table(u'survey_question')

        # Deleting model 'Submission'
        db.delete_table(u'survey_submission')

        # Deleting model 'Answer'
        db.delete_table(u'survey_answer')

        # Deleting model 'SurveyReport'
        db.delete_table(u'survey_surveyreport')

        # Deleting model 'SurveyReportDisplay'
        db.delete_table(u'survey_surveyreportdisplay')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'campaigns.areaits': {
            'Meta': {'object_name': 'AreaIts'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'campaigns.areamanager': {
            'Meta': {'object_name': 'AreaManager'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'campaigns.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'})
        },
        u'campaigns.channel': {
            'Meta': {'object_name': 'Channel'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'campaigns.event': {
            'Meta': {'object_name': 'Event'},
            'areamanager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.AreaManager']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Campaign']", 'null': 'True', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'districtmanager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.AreaIts']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'emailattachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'emailcontent': ('redactor.fields.RedactorField', [], {'null': 'True', 'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'eventtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.EventType']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'feedback': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'feedback_note': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'money': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'money_description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'payment': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'pointofsale': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'pointofsaledescription': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'population': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Province']", 'null': 'True', 'blank': 'True'}),
            'saleenddate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'salestartdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'salevalue': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'signups_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Theme']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'trainer': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'typepointofsale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.PointOfSaleType']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'campaigns.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'campaigns.newsletter': {
            'Meta': {'object_name': 'Newsletter'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Campaign']"}),
            'content': ('redactor.fields.RedactorField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Event']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'startdate': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'testcontact': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        u'campaigns.pointofsaletype': {
            'Meta': {'object_name': 'PointOfSaleType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'campaigns.theme': {
            'Meta': {'object_name': 'Theme'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'contacts.company': {
            'Meta': {'object_name': 'Company'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'civic': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Province']", 'null': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'vat': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20', 'primary_key': 'True'})
        },
        u'contacts.contact': {
            'Meta': {'object_name': 'Contact'},
            'action_subdivision': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contact_action_subdivision'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['contacts.SubDivision']"}),
            'anagrafic_subdivision': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'contact_anagrafic_subdivision'", 'blank': 'True', 'to': u"orm['contacts.SubDivision']"}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'civic': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16', 'primary_key': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Company']", 'null': 'True', 'blank': 'True'}),
            'company_ranking': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'participation_ranking': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'privacy_consensus': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Province']", 'null': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'I'", 'max_length': '1'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Work']", 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'})
        },
        u'contacts.division': {
            'Meta': {'object_name': 'Division'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'contacts.province': {
            'Meta': {'ordering': "['code']", 'object_name': 'Province'},
            'capital': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'coat': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Region']"})
        },
        u'contacts.region': {
            'Meta': {'ordering': "['name']", 'object_name': 'Region'},
            'coat': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'special': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'contacts.sector': {
            'Meta': {'object_name': 'Sector'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'contacts.subdivision': {
            'Meta': {'object_name': 'SubDivision'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Division']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'contacts.work': {
            'Meta': {'object_name': 'Work'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Sector']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'survey.answer': {
            'Meta': {'ordering': "('question',)", 'object_name': 'Answer'},
            'boolean_answer': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'flickr_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'float_answer': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_answer': ('survey.fields.ImageWithThumbnailsField', [], {'max_length': '500', 'blank': 'True'}),
            'integer_answer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'photo_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['survey.Question']"}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['survey.Submission']"}),
            'text_answer': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'survey.question': {
            'Meta': {'object_name': 'Question'},
            'answer_is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'correct_answer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'fieldname': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {}),
            'numeric_is_int': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'option_type': ('django.db.models.fields.CharField', [], {'max_length': '14'}),
            'options': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'question': ('django.db.models.fields.TextField', [], {}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': u"orm['survey.Survey']"}),
            'use_as_filter': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'survey.submission': {
            'Meta': {'ordering': "('-submitted_at',)", 'object_name': 'Submission'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']", 'null': 'True', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'submitted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['survey.Survey']"})
        },
        u'survey.survey': {
            'Meta': {'object_name': 'Survey'},
            'allow_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_multiple_submissions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_voting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'archive_policy': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'default_report': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reports'", 'null': 'True', 'to': u"orm['survey.SurveyReport']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'ends_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_event'", 'null': 'True', 'to': u"orm['campaigns.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'moderate_submissions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_newsletter'", 'null': 'True', 'to': u"orm['campaigns.Newsletter']"}),
            'require_login': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'starts_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'survey_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'tease': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'thanks': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'survey.surveyreport': {
            'Meta': {'object_name': 'SurveyReport'},
            'display_individual_results': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_the_filters': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_results_to': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sort_by_rating': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['survey.Survey']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'survey.surveyreportdisplay': {
            'Meta': {'ordering': "('order',)", 'object_name': 'SurveyReportDisplay'},
            'aggregate_type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'annotation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'caption_fields': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'display_type': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'fieldnames': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_map_answers': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'map_center_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'map_center_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'map_zoom': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['survey.SurveyReport']"}),
            'x_axis_fieldname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        }
    }

    complete_apps = ['survey']