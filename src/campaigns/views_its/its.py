from django.db.models import Q
from django.template import RequestContext
from backend.utils import is_its
from campaigns.models import Event
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test


@user_passes_test(is_its)
def view_agenda(request):
    return render_to_response('admin/its/view_agenda.html', {},
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
            target['color'] = 'black'
            target['borderColor'] = 'red'
            target['backgroundColor'] = 'orange'

        targets_json.append(target)
    response_data = {'value': 'OK', 'message': 'lista', 'targets': targets_json}
    return HttpResponse(json.dumps(response_data), mimetype="application/json")

