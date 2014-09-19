import os
import re

import xlrd
import xlwt
from geopy.geocoders import GoogleV3
import Levenshtein

from django.core.management.base import BaseCommand, CommandError

from campaigns.models import PointOfSaleType
from contacts.models import Company, Province


B_PARTNER_FIELD = 'B_partner'
NOME_1_FIELD = 'Nome_1'
NOME_2_FIELD = 'Nome_2'
PIVA_FIELD = 'Partita_iva'
VIA_FIELD = 'Via'
CAP_FIELD = 'CAP'
CITY_FIELD = 'Citta'
FIELDS = {B_PARTNER_FIELD: 0, NOME_1_FIELD: 1,
          NOME_2_FIELD: 2, PIVA_FIELD: 3,
          VIA_FIELD: 5, CAP_FIELD: 6, CITY_FIELD: 7}

CAP_REGEX = re.compile(r'^[0-9]{5}$')
PROVINCE_REGEX = re.compile(r'[A-Z]{2},')
geolocator = GoogleV3(domain='maps.google.it')

def _find_province_obj(city, postal_code):

    province = None
    province_id = -1
    province_code = ''
    if postal_code and CAP_REGEX.match(postal_code):
        location = geolocator.geocode('%s, %s, Italia' % (city, postal_code))
        '''
        location.address can have the form:
        u'Ischia Porto, 80077 Ischia NA, Italia'
        u'Galliera Veneta PD, Italia'
        u'25074 Idro BS, Italia'
        u'00183 Roma, Italia'
        '''
        match = PROVINCE_REGEX.search(location.address)
        if match:
            province_code = match.group(0).replace(',', '')
            if province_code in ('ROMA', 'Roma', 'roma'):
                province_code = 'RM'
            province_qs = Province.objects.filter(code=province_code)
            if province_qs:
                province = province_qs[0]
                province_id = province.id
                province_code = province.code
        else:
            province_qs = Province.objects.filter(name=city)
            if province_qs:
                province = province_qs[0]
                province_id = province.id
                province_code = province.code
            else:
                print 'Provincia non trovata...%s %s' % (city, postal_code)

    return province, province_id


def _extract_civic(street):
    civic = ''
    chunks = street.split()
    if chunks:
        civic = chunks[-1][:5]  # should be the last word in street (max 5 chars)
        street = ' '.join([c for c in chunks[0:-1]])
    for _ in ('N.', 'n.', 'NR.', 'Nr.', 'NR', 'Nr', 'nr'):
        if _ in civic:
            civic = civic.replace(_, '').strip()
            break
    for _ in ("Sant'", "San ", "Santa ", "SANT'", "SAN ", "SANTA "):
        if _ in street:
            street = street.replace(_, 'S.').strip()
            break
    return street, civic


def _are_similar(s1, s2):
    ratio = Levenshtein.ratio(s1.upper(), s2.upper())
    return ratio >= 0.8


def _is_duplicate(company_dict):
    # find same vat
    if Company.objects.filter(vat=company_dict['vat']):
        return True
    # find same company code
    if Company.objects.filter(company_code=company_dict['code']):
        return True
    if company_dict['province']:
        # find similar name, same city and check if addresses are very similar
        # extra_where = ["`contacts_company`.`province_id`=%s", "LOWER(%s) LIKE LOWER(CONCAT('%%', `contacts_company`.`name`, '%%')) OR LOWER(`contacts_company`.`name`) LIKE LOWER('%%%s%%'))"]
        # extra_params = [company_dict['province_id'], company_dict['name'], company_dict['name']]
        candidates = Company.objects.filter(province=company_dict['province'], city=company_dict['city'], civic=company_dict['civic'])
        for c in candidates:
            if _are_similar(c.street, company_dict['street']):
                return True
    return False


def _guess_company_type(company_name):
    t = None
    # TODO check more types
    if company_name.find('F.CIA') > -1 or company_name.find('FARMACIA') > -1:
        t = PointOfSaleType.objects.get(description='FARMACIA')
    return t


def _save_company(company_dict):
    company = Company()
    company.vat = company_dict['vat'].strip()
    company.name = company_dict['company_name'].strip().title()
    company.company_code = company_dict['code'].strip()
    company.city = company_dict['city'].strip()
    company.street = company_dict['street'].strip().title()
    company.civic = company_dict['civic'].strip()
    company.province = company_dict['province']
    company.type = _guess_company_type(company_dict['company_name'].strip())
    company.save()


def _log(param):
    print param


def copy_row_between_sheet(sheet, row, discarded_sheet, row_disc, extra=''):
    for col in xrange(0, sheet.ncols):
        discarded_sheet.write(row_disc, col, sheet.cell(row, col).value)
    if extra:
        #add an extra column (e.g. for logging messages)
        discarded_sheet.write(row_disc, sheet.ncols, extra)
        _log('Riga %d: azienda scartata per motivo: %s.' % (row + 1, extra))


class Command(BaseCommand):
    args = '</path/to/export_aziende.xls>'
    help = "Import Companies (Aziende) in ENS database from xls"

    def handle(self, *args, **options):

        if not args:
            raise CommandError('Parametro filename.xls mancante')
        filename = os.path.abspath(args[0])
        discarded_filename = os.path.abspath('%s_%s' % (args[0], 'discarded.xls'))
        xls = xlrd.open_workbook(filename)
        discarded_wb = xlwt.Workbook()
        discarded_sheet = discarded_wb.add_sheet('Aziende non inserite')
        sheet = xls.sheet_by_index(0)
        # copy header
        copy_row_between_sheet(sheet, 0, discarded_sheet, 0)
        counter = 0
        discarded = 0

        #skip header
        for row in xrange(1, sheet.nrows):
            company_code = sheet.cell(row, FIELDS[B_PARTNER_FIELD]).value
            if not company_code:
                copy_row_between_sheet(sheet, row, discarded_sheet, discarded + 2, extra='Codice azienda mancante')
                discarded += 1
                continue
            vat = sheet.cell(row, FIELDS[PIVA_FIELD]).value
            if not vat:
                copy_row_between_sheet(sheet, row, discarded_sheet, discarded + 2, extra='PIVA mancante')
                discarded += 1
                continue
            name_1 = sheet.cell(row, FIELDS[NOME_1_FIELD]).value
            name_2 = sheet.cell(row, FIELDS[NOME_2_FIELD]).value
            street = sheet.cell(row, FIELDS[VIA_FIELD]).value
            city = sheet.cell(row, FIELDS[CITY_FIELD]).value
            postal_code = sheet.cell(row, FIELDS[CAP_FIELD]).value

            company_name = '%s - %s' % (name_1, name_2) if name_2 else name_1
            street, civic = _extract_civic(street)

            province, province_id = _find_province_obj(city, postal_code)
            company_dict = {'company_name': company_name, 'name': name_1, 'code': company_code, 'street': street, 'civic': civic,
                            'city': city, 'vat': vat, 'province': province, 'province_id': province_id}

            if _is_duplicate(company_dict):
                copy_row_between_sheet(sheet, row, discarded_sheet, discarded + 2, extra='Duplicato')
                discarded += 1
                continue

            # Everything is ok. A new Company can be inserted
            _save_company(company_dict)
            counter += 1

        # end for
        # write discarded xls

        discarded_wb.save(discarded_filename)
        _log('>>>>>>> Import terminato')
        _log('>>Aziende inserite: %d' % counter)
        _log('>>Aziende scartate: %d (controllare il file %s)' % (discarded, discarded_filename))
