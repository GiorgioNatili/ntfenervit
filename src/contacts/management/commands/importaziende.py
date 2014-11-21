import os
import re
import sys

import xlrd
import xlwt
import Levenshtein

from django.core.management.base import BaseCommand, CommandError

from campaigns.models import PointOfSaleType
from contacts.models import Company, Province

COMPANY_TYPES = {'0100': PointOfSaleType.objects.get(description='FARMACIA'),
                 '0150': PointOfSaleType.objects.get(description='FARMACIA'),
                 '0025': PointOfSaleType.objects.get(description='FARMACIA'),
                 '0050': PointOfSaleType.objects.get(description='FARMACIA'),
                 '0800': PointOfSaleType.objects.get(description='FARMACIA'),
                 '0700': PointOfSaleType.objects.get(description='PARAFARMACIA'),
                 '0750': PointOfSaleType.objects.get(description='PARAFARMACIA'),
                 '8200': PointOfSaleType.objects.get(description='MEDICO'),
                 '0600': PointOfSaleType.objects.get(description='ERBORISTERIA'),
                 '0650': PointOfSaleType.objects.get(description='ERBORISTERIA'),
                 '1100': PointOfSaleType.objects.get(description='OSPEDALE'),
                 '1300': PointOfSaleType.objects.get(description='OSPEDALE'),
                 '2100': PointOfSaleType.objects.get(description='FARMACIA'),
                 '2300': PointOfSaleType.objects.get(description='FARMACIA'),
                 'N200': PointOfSaleType.objects.get(description='NEGOZIO DI INTEGRATORI'),
                 'O200': PointOfSaleType.objects.get(description='NEGOZIO DI INTEGRATORI'),
                 'O100': PointOfSaleType.objects.get(description='NEGOZIO DI INTEGRATORI'),
                 'O500': PointOfSaleType.objects.get(description='NEGOZIO DI INTEGRATORI'),
                 'P025': PointOfSaleType.objects.get(description='NEGOZIO DI INTEGRATORI'),
                 'P100': PointOfSaleType.objects.get(description='NEGOZIO DI INTEGRATORI'),
                 'P000': PointOfSaleType.objects.get(description='SOC. SPORTIVA'),
                 }
B_PARTNER_FIELD = 'CdBP'
NOME_1_FIELD = 'name_1'
NOME_2_FIELD = 'name_2'
PIVA_FIELD = 'vad_it_no'
VIA_FIELD = 'street'
CITY_FIELD = 'city_1'
PROV_FIELD = 'district'
EMAIL_FIELD = 'email'
POS_TYPE_FIELD = 'CdCatVe'
USER_PIVA_FIELD = 'user_ind_1'
FIELDS = {B_PARTNER_FIELD: 2, NOME_1_FIELD: 3,
          NOME_2_FIELD: 4, PIVA_FIELD: 8,
          USER_PIVA_FIELD: 9, POS_TYPE_FIELD: 11,
          VIA_FIELD: 5, CITY_FIELD: 6,
          PROV_FIELD: 7, EMAIL_FIELD: 10}

CAP_REGEX = re.compile(r'^[0-9]{5}$')
PROVINCE_REGEX = re.compile(r'^[A-Z]{2}$,')


def _sort_street_civic(street):
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
        candidates = Company.objects.filter(province=company_dict['province'], city=company_dict['city'], civic=company_dict['civic'])
        for c in candidates:
            if _are_similar(c.street, company_dict['street']):
                return True
    return False


def _save_company(company_dict):
    company = Company()
    company.vat = company_dict['vat'].strip()
    company.name = company_dict['company_name'].strip().title()
    company.company_code = company_dict['code'].strip()
    company.city = company_dict['city'].strip()
    company.street = company_dict['street'].strip().title()
    company.civic = company_dict['civic'].strip()
    company.province = company_dict['province']
    company.type = COMPANY_TYPES.get(company_dict['company_typecode'].strip(), PointOfSaleType.objects.get(description='ALTRO'))
    company.save()


def _log(param):
    print param


def copy_row_between_sheets(sheet, row, discarded_sheet, row_disc, extra=''):
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
            raise CommandError('Parametro filename excel mancante')
        if args[0] == 'clean':
            Company.objects.exclude(name__icontains='ENERVIT').delete()
            _log('>>>>>>> Clean terminato')
            sys.exit(0)
        filename = os.path.abspath(args[0])
        discarded_filename = os.path.abspath('%s_%s' % (args[0], 'discarded.xls'))
        xls = xlrd.open_workbook(filename)
        discarded_wb = xlwt.Workbook()
        discarded_sheet = discarded_wb.add_sheet('Aziende non inserite')
        sheet = xls.sheet_by_index(0)
        # copy header
        copy_row_between_sheets(sheet, 0, discarded_sheet, 0)
        counter = 0
        discarded = 0

        #skip header
        for row in xrange(1, sheet.nrows):
            company_code = sheet.cell(row, FIELDS[B_PARTNER_FIELD]).value
            if not company_code:

                copy_row_between_sheets(sheet, row, discarded_sheet, discarded + 2, extra='Codice azienda mancante')
                discarded += 1
                continue
            vat = sheet.cell(row, FIELDS[PIVA_FIELD]).value
            if not vat:
                #fallback to personal PIVA if exists
                user_piva = sheet.cell(row, FIELDS[USER_PIVA_FIELD]).value
                if not user_piva:
                    copy_row_between_sheets(sheet, row, discarded_sheet, discarded + 2, extra='PIVA mancante')
                    discarded += 1
                    continue
                vat = user_piva
            try:
                name_1 = sheet.cell(row, FIELDS[NOME_1_FIELD]).value.strip().strip('*')
                name_2 = sheet.cell(row, FIELDS[NOME_2_FIELD]).value.strip()
                street = sheet.cell(row, FIELDS[VIA_FIELD]).value.strip()
                city = sheet.cell(row, FIELDS[CITY_FIELD]).value.strip()
                province = sheet.cell(row, FIELDS[PROV_FIELD]).value.strip()
                province_obj = Province.objects.get(code=province.strip()) if province else None
                point_of_sale_type = sheet.cell(row, FIELDS[POS_TYPE_FIELD]).value.strip()
                email = sheet.cell(row, FIELDS[EMAIL_FIELD]).value
            except Exception, e:
                copy_row_between_sheets(sheet, row, discarded_sheet, discarded + 2, extra=e.message)
                discarded += 1
                continue
            company_name = '%s - %s' % (name_1, name_2) if name_2 else name_1
            street, civic = _sort_street_civic(street)

            company_dict = {'company_name': company_name, 'name': name_1,
                            'code': company_code, 'street': street, 'civic': civic,
                            'city': city, 'vat': vat, 'company_typecode': point_of_sale_type,
                            'province': province_obj, 'email': email}

            if _is_duplicate(company_dict):
                copy_row_between_sheets(sheet, row, discarded_sheet, discarded + 2, extra='Duplicato')
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
