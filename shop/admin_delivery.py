"""
Module E — Delivery Admin Configuration
Integrates with Django Unfold for the admin interface.

To integrate: add these imports and registrations to shop/admin.py
or import this file from shop/admin.py.
"""

from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin
from unfold.decorators import action

from shop.models_delivery import Delivery


@admin.action(description='Confirm selected deliveries')
def confirm_deliveries(modeladmin, request, queryset):
    """
    Admin action: confirm delivery for selected records.
    Sets confirmed=True and delivery_date to today if not set.
    Updates associated order status to 'delivered'.
    """
    today = timezone.now().date()
    for delivery in queryset.filter(confirmed=False):
        if not delivery.delivery_date:
            delivery.delivery_date = today
        delivery.confirmed = True
        delivery.save()
        # Update order status
        order = delivery.order
        order.status = 'delivered'
        order.save(update_fields=['status', 'updated_at'])


@admin.register(Delivery)
class DeliveryAdmin(ModelAdmin):
    """
    Admin interface for managing deliveries.
    Supports Workflow 3: Steps 4–6.
    """

    list_display = [
        'id',
        'order_link',
        'customer_name',
        'method',
        'delivery_date',
        'confirmed',
        'created_at',
    ]
    list_filter = [
        'confirmed',
        'method',
        'delivery_date',
    ]
    search_fields = [
        'order__id',
        'recipient_name',
        'order__customer__first_name',
        'order__customer__last_name',
    ]
    list_editable = ['confirmed']
    readonly_fields = ['created_at']
    autocomplete_fields = ['order']
    actions = [confirm_deliveries]

    fieldsets = (
        ('Order Information', {
            'fields': ('order',),
        }),
        ('Delivery Details', {
            'fields': ('method', 'delivery_date', 'recipient_name'),
        }),
        ('Completion', {
            'fields': ('confirmed', 'final_observations'),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Order')
    def order_link(self, obj):
        return f'Order #{obj.order_id}'

    @admin.display(description='Customer')
    def customer_name(self, obj):
        customer = obj.order.customer
        return f'{customer.first_name} {customer.last_name}'
