# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'EventType.contact_to_customer'
        db.add_column(u'campaigns_eventtype', 'contact_to_customer',
                      self.gf('django.db.models.fields.FloatField')(default=1),
                      keep_default=False)

        # Adding field 'EventType.customer_to_sale'
        db.add_column(u'campaigns_eventtype', 'customer_to_sale',
                      self.gf('django.db.models.fields.FloatField')(default=1),
                      keep_default=False)

        # Adding field 'EventType.selectable'
        db.add_column(u'campaigns_eventtype', 'selectable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'EventType.contact_to_customer'
        db.delete_column(u'campaigns_eventtype', 'contact_to_customer')

        # Deleting field 'EventType.customer_to_sale'
        db.delete_column(u'campaigns_eventtype', 'customer_to_sale')

        # Deleting field 'EventType.selectable'
        db.delete_column(u'campaigns_eventtype', 'selectable')


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
        u'campaigns.eventcoupon': {
            'Meta': {'object_name': 'EventCoupon'},
            'coupon': ('django.db.models.fields.CharField', [], {'max_length': '14'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'campaigns.eventpayment': {
            'Meta': {'object_name': 'EventPayment'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']", 'null': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Event']", 'null': 'True'}),
            'executor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Province']", 'null': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'vat': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'way': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True'})
        },
        u'campaigns.eventsignup': {
            'Meta': {'object_name': 'EventSignup'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']"}),
            'coupon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coupon.Coupon']", 'null': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'omaggio': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pagante': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'presence': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'relatore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'relatore_payment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'campaigns.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'contact_to_customer': ('django.db.models.fields.FloatField', [], {}),
            'customer_to_sale': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selectable': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'campaigns.goal': {
            'Meta': {'object_name': 'Goal'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'campaigns.image': {
            'Meta': {'object_name': 'Image'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_image': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
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
        u'campaigns.newsletterattachment': {
            'Meta': {'object_name': 'NewsletterAttachment'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Newsletter']"})
        },
        u'campaigns.newsletterschedulation': {
            'Meta': {'object_name': 'NewsletterSchedulation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Newsletter']"}),
            'report_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'send_date': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'})
        },
        u'campaigns.newslettertarget': {
            'Meta': {'object_name': 'NewsletterTarget'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Newsletter']"})
        },
        u'campaigns.newslettertemplate': {
            'Meta': {'object_name': 'NewsletterTemplate'},
            'content': ('redactor.fields.RedactorField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'campaigns.pointofsaletype': {
            'Meta': {'object_name': 'PointOfSaleType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'campaigns.survey': {
            'Meta': {'object_name': 'Survey'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Newsletter']"})
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
        u'coupon.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']", 'null': 'True'}),
            'coupon_bulk': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'coupons'", 'to': u"orm['coupon.CouponSet']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'coupon.couponset': {
            'Meta': {'object_name': 'CouponSet'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaigns.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_date': ('django.db.models.fields.DateField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['campaigns']