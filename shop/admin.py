"""
Costuras de Paqui - Admin Configuration
========================================

Each member fills in ONLY their assigned section.
The basic registrations below make the admin work immediately;
each member should replace their stub with a richer ModelAdmin class.

OWNERSHIP:
  Member 1 -> Customer
  Member 2 -> Order, OrderItem
  Member 3 -> Garment, Measurement, Material
  Member 4 -> Employee, WorkTicket, ProductionLog
  Member 5 -> Delivery
"""
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display

from .models import (
    Customer,
    Order, OrderItem,
    Garment, Measurement, Material,
    Employee, WorkTicket, ProductionLog,
    Delivery,
)


# ============================================================
# MEMBER 1 - Customer
# ============================================================
# TODO Member 1: Build out CustomerAdmin
#   - list_display: full name, phone, email, created_at
#   - search_fields: first_name, last_name, phone, email
#   - Optional: inline showing this customer's orders (read-only)

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'email', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    list_filter = ['created_at']


# ============================================================
# MEMBER 2 - Order, OrderItem
# ============================================================
# TODO Member 2: Build out OrderAdmin
#   - OrderItemInline (TabularInline) for adding garments while creating order
#   - list_display: id, customer, order_date, due_date, status, total_price
#   - list_filter: status, due_date, order_date
#   - search_fields: customer__first_name, customer__last_name
#   - Admin action: "Mark selected orders as confirmed"

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ['garment']


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['id', 'customer', 'order_date', 'due_date', 'status_badge', 'items_display', 'total_price_display']
    list_filter = ['status', 'due_date', 'order_date']
    search_fields = ['customer__first_name', 'customer__last_name', 'id']
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']
    actions = ['mark_as_confirmed']

    @display(description='Items')
    def items_display(self, obj):
        count = obj.items.count()
        return f"{count} item{'s' if count != 1 else ''}"

    @display(description='Total', ordering='total_price')
    def total_price_display(self, obj):
        return f"€{obj.total_price:,.2f}"

    @display(
        description='Status',
        ordering='status',
        label={
            'received': 'info',
            'confirmed': 'info',
            'in_production': 'warning',
            'ready_for_delivery': 'success',
            'delivered': 'success',
            'cancelled': 'danger',
        },
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @admin.action(description='Mark selected orders as confirmed')
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} order(s) marked as confirmed.')

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ['id', 'order', 'garment', 'quantity', 'unit_price']
    search_fields = ['order__id', 'garment__garment_type']


# ============================================================
# MEMBER 3 - Garment, Measurement, Material
# ============================================================
# TODO Member 3: Build out GarmentAdmin
#   - MeasurementInline (StackedInline) for the 1:1 relation
#     NOTE: Inline OneToOne is tricky. Easier alternative: keep Measurement
#     as a separate admin and use autocomplete_fields = ['measurement'] on Garment.
#   - filter_horizontal = ['materials'] for the M:N
#   - list_display: garment_type, color, priority, status
#   - list_filter: status, priority, garment_type
#
# TODO Member 3: Build out MaterialAdmin
#   - list_display with stock_meters
#   - list_filter on fabric_type
#   - Add visual indicator when stock_meters < 5 (low stock)

@admin.register(Garment)
class GarmentAdmin(ModelAdmin):
    list_display = ['id', 'garment_type', 'color', 'priority_badge', 'status_badge', 'created_at']
    list_filter = ['status', 'priority', 'garment_type']
    search_fields = ['garment_type', 'color']
    filter_horizontal = ['materials']
    autocomplete_fields = ['measurement']

    @display(
        description='Status',
        ordering='status',
        label={
            'pending': 'info',
            'in_production': 'warning',
            'completed': 'success',
            'on_hold': 'danger',
        },
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @display(
        description='Priority',
        ordering='priority',
        label={
            'normal': 'info',
            'urgent': 'warning',
            'rush': 'danger',
        },
    )
    def priority_badge(self, obj):
        return obj.priority, obj.get_priority_display()


@admin.register(Measurement)
class MeasurementAdmin(ModelAdmin):
    list_display = ['id', 'bust', 'waist', 'hips', 'total_length']
    search_fields = ['extra_notes']


@admin.register(Material)
class MaterialAdmin(ModelAdmin):
    list_display = ['name', 'fabric_type', 'color', 'stock_meters', 'price_per_meter']
    list_filter = ['fabric_type']
    search_fields = ['name', 'color']


# ============================================================
# MEMBER 4 - Employee, WorkTicket, ProductionLog
# ============================================================
# TODO Member 4:
#   - EmployeeAdmin with list_filter on is_active and role
#   - WorkTicketAdmin: limit assigned_to dropdown to active employees
#     (override formfield_for_foreignkey)
#   - ProductionLogAdmin: make immutable (override get_readonly_fields when
#     obj exists, override has_delete_permission)
#   - Optional admin action: "Advance ticket to next stage" (creates a
#     ProductionLog row automatically)
@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ['first_name', 'last_name', 'role', 'specialization', 'is_active']
    list_filter = ['is_active', 'role']
    search_fields = ['first_name', 'last_name', 'role']
    
@admin.register(WorkTicket)
class WorkTicketAdmin(ModelAdmin):
    list_display = ['id', 'garment', 'assigned_to', 'stage_badge', 'priority_badge', 'deadline']
    list_filter = ['current_stage', 'priority']
    search_fields = ['id', 'garment__garment_type']
    autocomplete_fields = ['garment', 'assigned_to']

    @display(
        description='Stage',
        ordering='current_stage',
        label={
            'order_received': 'info',
            'design_confirmed': 'info',
            'cutting': 'warning',
            'sewing': 'warning',
            'finishing': 'warning',
            'quality_check': 'warning',
            'ready_for_delivery': 'success',
            'rework': 'danger',
        },
    )
    def stage_badge(self, obj):
        return obj.current_stage, obj.get_current_stage_display()

    @display(
        description='Priority',
        ordering='priority',
        label={
            'normal': 'info',
            'urgent': 'warning',
            'rush': 'danger',
        },
    )
    def priority_badge(self, obj):
        return obj.priority, obj.get_priority_display()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Business Rule 5: only active employees can be assigned to new tickets
        if db_field.name == 'assigned_to':
            kwargs['queryset'] = Employee.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



# Reusable color map for ticket stages (used by ProductionLogAdmin too)
TICKET_STAGE_LABELS = {
    'order_received': 'info',
    'design_confirmed': 'info',
    'cutting': 'warning',
    'sewing': 'warning',
    'finishing': 'warning',
    'quality_check': 'warning',
    'ready_for_delivery': 'success',
    'rework': 'danger',
}


@admin.register(ProductionLog)
class ProductionLogAdmin(ModelAdmin):
    list_display = ['id', 'ticket', 'from_stage_badge', 'to_stage_badge', 'performed_by', 'timestamp']
    list_filter = ['to_stage', 'timestamp']
    search_fields = ['ticket__id', 'comments']

    @display(description='From', ordering='from_stage', label=TICKET_STAGE_LABELS)
    def from_stage_badge(self, obj):
        if not obj.from_stage:
            return None, '—'
        return obj.from_stage, obj.get_from_stage_display()

    @display(description='To', ordering='to_stage', label=TICKET_STAGE_LABELS)
    def to_stage_badge(self, obj):
        return obj.to_stage, obj.get_to_stage_display()

    def get_readonly_fields(self, request, obj=None):
        # Business Rule 9: production log entries are immutable once created
        if obj:
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# MEMBER 5 - Delivery
# ============================================================
# TODO Member 5: Build out DeliveryAdmin
#   - list_display: order, delivery_date, method, recipient_name, confirmed
#   - list_filter: method, confirmed, delivery_date
#   - search_fields: order__id, recipient_name

@admin.register(Delivery)
class DeliveryAdmin(ModelAdmin):
    list_display = ['order', 'delivery_date', 'method', 'recipient_name', 'confirmed']
    list_filter = ['method', 'confirmed', 'delivery_date']
    search_fields = ['order__id', 'recipient_name']
    autocomplete_fields = ['order']
