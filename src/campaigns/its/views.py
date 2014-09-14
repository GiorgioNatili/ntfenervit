from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

from campaigns.models import Event, District, ITSRelConsultant, ITSRelDistrict, is_its
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
        target['campaign'] = e.campaign.name
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

@user_passes_test(is_its)
def view_report(request, year=None):
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

    if year:
        # Generate report
        params["year"] = int(year)
        rpt = ConsumerReport(year, district_id=district_id, its_id=its_id, consultant_id=consultant_id)
        if len(rpt.rows):
            params["rpt_consumer"] = rpt
            params["rpt_revenue"] = RevenueReport(params["rpt_consumer"].total_sales)
            params["show_report"] = True
        else:
            params["nodata"] = True

    return render_to_response('admin/its/view_report.html', params,
                              context_instance=RequestContext(request))