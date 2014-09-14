from django.db.models import Q
from django.template import RequestContext
from backend.utils import is_backend_admin
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

from campaigns.models import is_its
import xlwt

from campaigns.models import Event, District, ITSRelDistrict, ITSRelConsultant
from .report_helper import ListOfYear, ConsumerReport, RevenueReport


@user_passes_test(is_its)
def view_agenda(request):
    return render_to_response('admin/its/view_agenda.html', {},
                              context_instance=RequestContext(request))


@user_passes_test(is_its)
def view_eventlist(request):
    user = request.user
    events = Event.objects.filter(Q(owner=user) | Q(its_districtmanager=user))
    #monkey patching for differentiate events not owned but assigned to
    for e in events:
        e.not_owned = True if not user == e.owner else False
    return render_to_response('admin/its/view_event.html', {'events': events},
                              context_instance=RequestContext(request))


def view_eventlist_rest(request):
    user = request.user
    events = Event.objects.filter(Q(visible_for_its=True) | Q(owner=user) | Q(its_districtmanager=user))
    import json
    targets_json = []
    for e in events:
        target = {'id': e.id, 'start': str(e.date), 'end': str(e.enddate)}
        if e.enddate is None:
            target['end'] = target['start']
        target['title'] = e.description
        if e.title:
            target['title'] = e.title
        target['campaign'] = e.campaign.name if e.campaign else None
        target['url'] = '/admin/campaigns/event/'+str(e.id)
        if e.owner == user:
            target['url'] += '?from_its=1'
            target['backgroundColor'] = 'red'
            target['color'] = 'white'
            target['borderColor'] = 'yellow'
        elif e.its_districtmanager == user:
            # these events appears on the its user agenda
            # but they were created by admins
            # and assigned to them as public events
            target['color'] = 'black'
            target['borderColor'] = 'red'
            target['backgroundColor'] = 'orange'

        targets_json.append(target)
    response_data = {'value': 'OK', 'message': 'lista', 'targets': targets_json}
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


##################
### ITS Report ###
##################

def its_report_viewer(request, year, its_mode):
    list_year = ListOfYear()

    # Read QueryString, initializing with default
    district_id = -1
    its_id = -1
    consultant_id = "-1"
    if request.method == "GET":
        district_id = request.GET.get("district", district_id)
        its_id = request.GET.get("its", its_id)
        consultant_id = request.GET.get("consultant", consultant_id)

    # If list of year returns empty, show the no data page
    if len(list_year.rows) == 0:
        return render_to_response(
            'admin/its/view_report_nodata.html', {},
            context_instance=RequestContext(request)
        )
    else:
        params = {
            "years": [col[0] for col in list_year.rows],
            "districts": District.objects.all(),
            "district_id": district_id,
            "its_rels": ITSRelDistrict.objects.all(),
            "its_id": its_id,
            "consultant_rels": ITSRelConsultant.objects.all(),
            "consultant_id": consultant_id
        }
        if its_mode:
            user = request.user
            params["its_mode"] = True
            try:
                rel_district = ITSRelDistrict.objects.get(its=user)
            except ITSRelDistrict.DoesNotExist:
                rel_district = None

            if rel_district is None:
                params["its_error"] = "district.not.assigned"
                params["district_name"] = "Distretto NON Assegnato"
                params["its_name"] = "%s %s" % (user.first_name, user.last_name)
            else:
                params["district_id"] = rel_district.district.id
                params["district_name"] = rel_district.district.description

                params["its_id"] = rel_district.its.id
                params["its_name"] = "%s %s" % (rel_district.its.first_name, rel_district.its.last_name)


    if year:
        # Generate report
        params["year"] = int(year)
        rpt = ConsumerReport(year, district_id=district_id, its_id=its_id, consultant_id=consultant_id)
        if len(rpt.rows):
            params["rpt_consumer"] = rpt
            params["rpt_revenue"] = RevenueReport(params["rpt_consumer"].total["sales"])
            params["show_report"] = True
            params["qs"] = request.META.get("QUERY_STRING")
        else:
            params["nodata"] = True

    return render_to_response('admin/its/view_report.html', params,
                              context_instance=RequestContext(request))

@user_passes_test(is_its)
def view_its_report_its_section(request, year=None):
    '''
    Report called from the "Agenda ITS > ITS Report"
    '''
    return its_report_viewer(request, year, its_mode=True)

@user_passes_test(is_backend_admin)
def view_its_report_report_section(request, year=None):
    '''
    Report called from the "Report > ITS"
    '''
    return its_report_viewer(request, year, its_mode=False)

###############################
### ITS Report Excel Export ###
###############################
def can_run_report_export(user):
    '''
    Custom permission for excel export
    '''
    return is_its(user) or is_backend_admin(user)


def write_worksheet(worksheet, cols, total_cols, report):
    ws_row = 0
    ws_col = 0

    # Create Header Row
    for col in cols:
        if col != "":
            worksheet.write(ws_row, ws_col, report.fields[col])
        ws_col += 1

    # Create rows
    for row in report.rows:
        ws_row += 1
        ws_col = 0
        for col in cols:
            worksheet.write(ws_row, ws_col, row[col])
            ws_col += 1

    # Create total
    ws_row += 1
    ws_col = 0
    for tcol in total_cols:
        if tcol.startswith("s:"):
            title = tcol.split(":")[1]
            worksheet.write(ws_row, ws_col, title)
        elif tcol != "":
            worksheet.write(ws_row, ws_col, report.total[tcol])
        ws_col += 1

    # Reset the trailing column increment
    if ws_col:
        ws_col -= 1

    # Report last position it was writen to
    return ws_row, ws_col

@user_passes_test(can_run_report_export)
def export_its_report(request, year):
    # Read QueryString, initializing with default
    district_id = -1
    its_id = -1
    consultant_id = "-1"
    if request.method == "GET":
        district_id = request.GET.get("district", district_id)
        its_id = request.GET.get("its", its_id)
        consultant_id = request.GET.get("consultant", consultant_id)

    # Create Excel Output
    wb = xlwt.Workbook()

    style_percent = xlwt.XFStyle()
    style_percent.num_format_str = "0.0%"


    # Sheet 1: Stima Contatti Lordi
    rpt_consumer = ConsumerReport(year, district_id=district_id, its_id=its_id, consultant_id=consultant_id)
    if len(rpt_consumer.rows):
        ws = wb.add_sheet("Stima Contatti Lordi")

        rpt_columns = ("description", "events", "contacts", "contact_to_customer", "customers")
        rpt_totals = ("s:TOTALE", "events", "contacts", "", "customers")
        write_worksheet(ws, rpt_columns, rpt_totals, rpt_consumer)

    # Sheet 2: Sintesi Numero Consumatori
    if len(rpt_consumer.rows):
        ws = wb.add_sheet("Sintesi Numero Consumatori")

        rpt_columns = ("description", "customers", "customer_to_sale", "sales")
        rpt_totals = ("s:TOTALE", "customers", "", "sales")
        row, col = write_worksheet(ws, rpt_columns, rpt_totals, rpt_consumer)
        ws.write(row + 1, col, rpt_consumer.pct_sales_to_customers, style=style_percent)

    # Sheet 3: Stima Fatturati
    rpt_revenue = RevenueReport(rpt_consumer.total["sales"])
    if len(rpt_revenue.rows):
        ws = wb.add_sheet("Stima Fatturati")

        rpt_columns = ("id", "description", "total_sales", "sell_in_alloc", "sell_in_amount", "revenue")
        rpt_totals = ("s:TOTALE FATTURATO", "", "", "", "", "revenue")
        row, col = write_worksheet(ws, rpt_columns, rpt_totals, rpt_revenue)

    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=its_report.xls'

    wb.save(response)
    return response

