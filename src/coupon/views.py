# coding=utf-8
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
import xlwt

from campaigns.models import Event, AreaIts
from coupon.forms import CouponSetForm
from coupon.models import Coupon, CouponSet
from django.contrib import messages


def write_sheet_couponset(couponset, wb):
    ws = wb.add_sheet('Serie %d assegnata a %s' % (couponset.id, couponset.owner))
    ws.write(0, 0, 'Owner')
    ws.write(0, 1, 'Coupon')
    ws.write(0, 2, 'Usato')
    ws.write(0, 3, 'Da')
    coupons = couponset.coupons.all()
    row = 1
    for coupon in coupons:
        ws.write(row, 0, '%s %s %s' % (couponset.owner.first_name,
                                       couponset.owner.last_name,
                                       couponset.owner.email))
        ws.write(row, 1, str(coupon))
        ws.write(row, 2, str(coupon.used))
        if coupon.used:
            ws.write(row, 3, '%s %s %s' % (coupon.assigned_to.name,
                                           coupon.assigned_to.surname,
                                           coupon.assigned_to.email))
        else:
            ws.write(row, 3, '')
        row += 1


@staff_member_required
def export_couponset(request, id_couponset):
    couponset = CouponSet.objects.get(pk=id_couponset)
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=esportazione_omaggi-evento-serie_coupon' + couponset.__unicode__() + '.xls'
    wb = xlwt.Workbook()
    write_sheet_couponset(couponset, wb)
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
        write_sheet_couponset(couponset, wb)
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
        form = CouponSetForm(request.POST)
        if form.is_valid():
            couponset = form.save()
            coupon_list = []
            for i in xrange(couponset.size):
                coupon = Coupon()
                coupon.coupon_bulk = couponset
                coupon_list.append(coupon)
            Coupon.objects.bulk_create(coupon_list)
            return redirect('view_couponbyevent', id_event)
    else:
        #NOT POST - new FORM
        form = CouponSetForm()
    event = get_object_or_404(Event, id=id_event)
    staff_users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
    return render_to_response('admin/campaigns/view_coupongenerate.html',
                              {'form': form, 'event': event, 'staff_users': staff_users},
                              context_instance=RequestContext(request))
