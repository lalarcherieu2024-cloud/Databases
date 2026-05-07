"""
Custom admin views for the shop app.
Currently: calendar view of orders by due_date.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_datetime

from .models import Order


# Color mapping that matches the status badges in admin.py
STATUS_COLORS = {
    'received':            '#3b82f6',  # blue
    'confirmed':           '#3b82f6',  # blue
    'in_production':       '#eab308',  # yellow
    'ready_for_delivery':  '#22c55e',  # green
    'delivered':           '#22c55e',  # green
    'cancelled':           '#ef4444',  # red
}


@staff_member_required
def calendar_view(request):
    """Render the calendar HTML page (FullCalendar mounts on it)."""
    return render(request, 'admin/calendar.html', {
        'title': 'Production Calendar',
    })


@staff_member_required
def calendar_events(request):
    """JSON feed for FullCalendar. Returns orders within the visible range."""
    start = request.GET.get('start')
    end = request.GET.get('end')

    qs = Order.objects.select_related('customer').all()

    # FullCalendar passes ISO datetime strings for the visible range
    if start:
        qs = qs.filter(due_date__gte=parse_datetime(start).date())
    if end:
        qs = qs.filter(due_date__lte=parse_datetime(end).date())

    events = []
    for order in qs:
        events.append({
            'id': order.pk,
            'title': f"#{order.pk} - {order.customer} ({order.get_status_display()})",
            'start': order.due_date.isoformat(),
            'allDay': True,
            'url': f"/admin/shop/order/{order.pk}/change/",
            'backgroundColor': STATUS_COLORS.get(order.status, '#6b7280'),
            'borderColor': STATUS_COLORS.get(order.status, '#6b7280'),
        })

    return JsonResponse(events, safe=False)