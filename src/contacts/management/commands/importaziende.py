import re
from django.db.models import Q
import xlrd
from geopy.geocoders import Nominatim
import Levenshtein

from django.core.management.base import BaseCommand, CommandError
from campaigns.models import PointOfSaleType

from contacts.models import Company, Province

geolocator = Nominatim()
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


def _find_province_obj(postal_code):

    province = None
    province_id = -1
    if postal_code and CAP_REGEX.match(postal_code):
        location = geolocator.geocode('%d Italia' % postal_code)
        chunks = location.address.split(', ')
        province_code = chunks[chunks.index(postal_code) - 2]
        if province_code in ('ROMA', 'Roma', 'roma'):
            province_code = 'RM'
        province_qs = Province.objects.filter(code=province_code)
        if province_qs:
            province = province_qs[0]
            province_id = province.code
    return province, province_id


def _extract_civic(street):
    civic = ''
    chunks = street.split()
    if chunks:
        civic = chunks[-1][:5]  # should be the last word in street (max 5 chars)
        street = ' '.join([c for c in chunks[0:-1]])
    return street, civic


def _are_similar(s1, s2):
    ratio = Levenshtein.ratio(s1, s2)
    return ratio >= 0.8


def _is_duplicate(company_dict):
    # find same vat
    if Province.objects.filter(vat=company_dict['vat']):
        return True
    # find same company code
    if Province.objects.filter(company_code=company_dict['code']):
        return True
    if company_dict['province']:
        # find similar name, same city and check if addresses are very similar
        extra_where = ["`contacts_company`.`province_id`=%s", "LOWER(%s) LIKE LOWER(CONCAT('%%', `contacts_company`.`name`, '%%')) OR LOWER(`contacts_company`.`name`) LIKE LOWER(CONCAT('%%', %s, '%%'))"]
        extra_params = [company_dict['province_id'], company_dict['name'], company_dict['name']]
        candidates = Company.objects.extra(where=extra_where, params=extra_params)
        for c in candidates:
            if c.city == company_dict['city'] and _are_similar(c.street, company_dict['street']):
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
    company.vat = company_dict['vat']
    company.name = company_dict['company_name']
    company.company_code = company_dict['code']
    company.city = company_dict['city']
    company.street = company_dict['street']
    company.civic = company_dict['civic']
    company.province = company_dict['province']
    company.type = _guess_company_type(company_dict['company_name'])
    company.save()


class Command(BaseCommand):
    args = '</path/to/export_aziende.xls>'
    help = "Import Companies (Aziende) in ENS database from xls"

    def handle(self, *args, **options):

        if not args:
            raise CommandError('Parametro filename.xls mancante')

        xls = xlrd.open_workbook(args[0])
        sheet = xls.sheet_by_index(0)
        counter = 0

        #skip header
        for row in xrange(1, sheet.nrows):
            company_code = sheet.cell(row, FIELDS[B_PARTNER_FIELD])
            if not company_code:
                #TODO to log and to write row in xls errors
                continue
            vat = sheet.cell(row, FIELDS[PIVA_FIELD])
            if not vat:
                #TODO to log 'company code has no vat' and to write row in xls errors
                continue
            name_1 = sheet.cell(row, FIELDS[NOME_1_FIELD])
            name_2 = sheet.cell(row, FIELDS[NOME_2_FIELD])
            street = sheet.cell(row, FIELDS[VIA_FIELD])
            city = sheet.cell(row, FIELDS[CITY_FIELD])
            postal_code = sheet.cell(row, FIELDS[CAP_FIELD])

            company_name = '%s - %s' % (name_1, name_2) if name_2 else name_1
            street, civic = _extract_civic(street)
            province, province_id = _find_province_obj(postal_code)
            company_dict = {'company_name': company_name, 'name': name_1, 'code': company_code, 'street': street, 'civic': civic,
                            'city': city, 'vat': vat, 'province': province, 'province_id': province_id}

            if _is_duplicate(company_dict):
                #TODO to log 'company code and row nr' and to write row in xls errors
                continue

            # Everything is ok. A new Company can be inserted
            _save_company(company_dict)
            counter += 1

        # end for
        # TODO to log end process and counter
