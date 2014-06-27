# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Company'
        db.create_table(u'contacts_company', (
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('vat', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20, primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, unique=True, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('civic', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('province', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Province'], null=True)),
        ))
        db.send_create_signal(u'contacts', ['Company'])

        # Adding model 'Region'
        db.create_table(u'contacts_region', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('special', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('coat', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'contacts', ['Region'])

        # Adding model 'Province'
        db.create_table(u'contacts_province', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Region'])),
            ('capital', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('coat', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'contacts', ['Province'])

        # Adding model 'Division'
        db.create_table(u'contacts_division', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'contacts', ['Division'])

        # Adding model 'SubDivision'
        db.create_table(u'contacts_subdivision', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Division'])),
        ))
        db.send_create_signal(u'contacts', ['SubDivision'])

        # Adding model 'Sector'
        db.create_table(u'contacts_sector', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'contacts', ['Sector'])

        # Adding model 'Work'
        db.create_table(u'contacts_work', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Sector'])),
        ))
        db.send_create_signal(u'contacts', ['Work'])

        # Adding model 'Visit'
        db.create_table(u'contacts_visit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Contact'])),
        ))
        db.send_create_signal(u'contacts', ['Visit'])

        # Adding model 'ChampionsDelivery'
        db.create_table(u'contacts_championsdelivery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Contact'])),
        ))
        db.send_create_signal(u'contacts', ['ChampionsDelivery'])

        # Adding model 'Payment'
        db.create_table(u'contacts_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Contact'])),
        ))
        db.send_create_signal(u'contacts', ['Payment'])

        # Adding model 'Contact'
        db.create_table(u'contacts_contact', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16, primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(default='m', max_length=1)),
            ('birthdate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('civic', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('province', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Province'], null=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Work'], null=True, blank=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.Company'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='I', max_length=1)),
            ('privacy_consensus', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('participation_ranking', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('company_ranking', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'contacts', ['Contact'])

        # Adding M2M table for field anagrafic_subdivision on 'Contact'
        m2m_table_name = db.shorten_name(u'contacts_contact_anagrafic_subdivision')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm[u'contacts.contact'], null=False)),
            ('subdivision', models.ForeignKey(orm[u'contacts.subdivision'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contact_id', 'subdivision_id'])

        # Adding M2M table for field action_subdivision on 'Contact'
        m2m_table_name = db.shorten_name(u'contacts_contact_action_subdivision')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm[u'contacts.contact'], null=False)),
            ('subdivision', models.ForeignKey(orm[u'contacts.subdivision'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contact_id', 'subdivision_id'])


    def backwards(self, orm):
        # Deleting model 'Company'
        db.delete_table(u'contacts_company')

        # Deleting model 'Region'
        db.delete_table(u'contacts_region')

        # Deleting model 'Province'
        db.delete_table(u'contacts_province')

        # Deleting model 'Division'
        db.delete_table(u'contacts_division')

        # Deleting model 'SubDivision'
        db.delete_table(u'contacts_subdivision')

        # Deleting model 'Sector'
        db.delete_table(u'contacts_sector')

        # Deleting model 'Work'
        db.delete_table(u'contacts_work')

        # Deleting model 'Visit'
        db.delete_table(u'contacts_visit')

        # Deleting model 'ChampionsDelivery'
        db.delete_table(u'contacts_championsdelivery')

        # Deleting model 'Payment'
        db.delete_table(u'contacts_payment')

        # Deleting model 'Contact'
        db.delete_table(u'contacts_contact')

        # Removing M2M table for field anagrafic_subdivision on 'Contact'
        db.delete_table(db.shorten_name(u'contacts_contact_anagrafic_subdivision'))

        # Removing M2M table for field action_subdivision on 'Contact'
        db.delete_table(db.shorten_name(u'contacts_contact_action_subdivision'))


    models = {
        u'contacts.championsdelivery': {
            'Meta': {'object_name': 'ChampionsDelivery'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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
        u'contacts.payment': {
            'Meta': {'object_name': 'Payment'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'})
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
        u'contacts.visit': {
            'Meta': {'object_name': 'Visit'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'contacts.work': {
            'Meta': {'object_name': 'Work'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Sector']"})
        }
    }

    complete_apps = ['contacts']