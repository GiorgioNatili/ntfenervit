from django.db.models import Q
from django.template import RequestContext
from backend.utils import is_its
from campaigns.models import Event
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

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
            # these events appears on the its_districtmanager user agenda
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
def view_report(request):

    # Read year params
    list_year = ListOfYear()
    if len(list_year.rows) == 0:
        return render_to_response(
            'admin/its/view_report_nodata.html', {},
            context_instance=RequestContext(request)
        )

    years = [col[0] for col in list_year.rows]
    try:
        year = int(request.GET.get('year'))
    except:
        year = years[0]

    params = {"years": years, "year": int(year), "rpt_consumer": ConsumerReport(year)}
    params["rpt_revenue"] = RevenueReport(params["rpt_consumer"].total_sales)

    return render_to_response('admin/its/view_report.html', params,
                              context_instance=RequestContext(request))