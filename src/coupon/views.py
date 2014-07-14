# coding=utf-8
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
import xlwt

from campaigns.models import Event, AreaIts
from coupon.models import Coupon, CouponSet
from django.contrib import messages

@staff_member_required
def export_couponset(request, id_couponset):
    cs = CouponSet.objects.get(pk=id_couponset)
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=esportazione_omaggi-evento-serie_coupon' + cs.__unicode__() + '.xls'

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Foglio 1')
    ws.write(0, 0, 'Omaggio')
    ws.write(0, 1, 'Usato')
    ws.write(0, 2, 'Da')

    coupons = cs.coupons.all()
    print len(coupons)
    row = 1
    for coupon in coupons:
        ws.write(row, 0, str(coupon))
        ws.write(row, 1, coupon.used)
        if coupon.used:
            ws.write(row, 2, coupon.assigned_to)
        else:
            ws.write(row, 2, '')
        row +=1
    wb.save(response)
    return response


@staff_member_required
def export_event_couponsets(request, id_event):
    event = get_object_or_404(Event, id=id_event)
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=esportazione_omaggi-evento-' + event.__unicode__() + '.xls'
    wb = xlwt.Workbook()

    couponsets = CouponSet.objects.filter(event=event)
    for couponset in couponsets:
        ws = wb.add_sheet('Serie coupon %d' % couponset.id)
        ws.write(0, 0, 'Omaggio')
        ws.write(0, 1, 'Usato')
        ws.write(0, 2, 'Da')
        row = 1
        for coupon in couponset.coupons.all():
            ws.write(row, 0, str(coupon))
            ws.write(row, 1, coupon.used)
            if coupon.used:
                ws.write(row, 2, coupon.assigned_to)
            else:
                ws.write(row, 2, '')
            row += 1

    wb.save(response)
    return response


@staff_member_required
def view_eventcoupon(request):
    events = Event.objects.all()
    return render_to_response('admin/campaigns/view_coupon.html',
                              {'events': events},
                              context_instance=RequestContext(request))

@staff_member_required
def view_couponbyevent(request, id_event):

    event = get_object_or_404(Event, id=id_event)
    coupon_sets = CouponSet.objects.all().filter(event=event)
    for cs in coupon_sets:
        cs.used = Coupon.objects.all().filter(coupon_bulk=cs, used=True).count()
    return render_to_response('admin/campaigns/view_couponbyevent.html',
                              {'event': event, 'coupon_sets': coupon_sets},
                              context_instance=RequestContext(request))



@staff_member_required
def delete_couponset(request, id_couponset, id_event):

    cs = CouponSet.objects.get(pk=id_couponset)
    used = Coupon.objects.all().filter(coupon_bulk=cs, used=True).count()

    if used > 0:
        Coupon.objects.all().filter(coupon_bulk=cs, used=False).delete()
        messages.warning(request, "Sono stati eliminati soltanto i coupon non utilizzati e non l'intera serie.")
    else:

        cs.delete()
        messages.info(request, "Serie coupon %s eliminata correttamente " % id_couponset)

    event = get_object_or_404(Event, id=id_event)
    coupon_sets = CouponSet.objects.all().filter(event=event)
    for cs in coupon_sets:
        cs.used = Coupon.objects.all().filter(coupon_bulk=cs, used=True).count()
    return redirect('view_couponbyevent', id_event)


@staff_member_required
def delete_coupon(request, id_coupon):
    coupon = Coupon.objects.get(pk=id_coupon)
    cs = coupon.coupon_bulk
    if coupon.used:
        messages.warning(request, "Coupon %s non cancellato perché già utilizzato da %s" % (coupon, coupon.assigned_to))
    else:
        coupon.delete()
        messages.info(request, "Il coupon %s è stato eliminato correttamente " % coupon)

    return redirect('view_couponset', cs.id, cs.event.id)

@staff_member_required
def view_couponset(request, id_couponset, id_event):
    event = get_object_or_404(Event, id=id_event)
    cs = get_object_or_404(CouponSet, id=id_couponset)
    coupons = Coupon.objects.filter(coupon_bulk=cs)
    return render_to_response('admin/campaigns/view_couponset_details.html',
                              {'event': event, 'coupon_set': cs, 'coupons': coupons},
                              context_instance=RequestContext(request))


@staff_member_required
def view_eventcoupon_generate(request, id_event):
    if request.method == 'POST':
        couponset = CouponSet()
        couponset.event = get_object_or_404(Event, id=id_event)
        couponset.its_area = get_object_or_404(AreaIts, id=request.REQUEST['its'])
        couponset.size = int(request.REQUEST['qt'])
        couponset.save()
        coupon_list = []
        for i in xrange(couponset.size):
            coupon = Coupon()
            coupon.coupon_bulk = couponset
            coupon_list.append(coupon)
        Coupon.objects.bulk_create(coupon_list)
        return redirect('view_couponbyevent', id_event)
    else:
        event = get_object_or_404(Event, id=id_event)
        its = AreaIts.objects.all()
    return render_to_response('admin/campaigns/view_coupongenerate.html', {'event': event, 'its': its},
                              context_instance=RequestContext(request))
