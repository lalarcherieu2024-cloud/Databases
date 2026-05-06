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
    list_display = ['id', 'customer', 'order_date', 'due_date', 'status', 'total_items', 'total_price']
    list_filter = ['status', 'due_date', 'order_date']
    search_fields = ['customer__first_name', 'customer__last_name', 'id']
    inlines = [OrderItemInline]
    autocomplete_fields = ['customer']
    actions = ['mark_as_confirmed']                                    

    def total_items(self, obj):                                        
        return obj.items.count()
    total_items.short_description = 'Items'                            

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
    list_display = ['id', 'garment_type', 'color', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'garment_type']
    search_fields = ['garment_type', 'color']
    filter_horizontal = ['materials']
    autocomplete_fields = ['measurement']


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
    list_display = ['id', 'garment', 'assigned_to', 'current_stage', 'priority', 'deadline']
    list_filter = ['current_stage', 'priority']
    search_fields = ['id', 'garment__garment_type']
    autocomplete_fields = ['garment', 'assigned_to']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Business Rule 5: only active employees can be assigned to new tickets
        if db_field.name == 'assigned_to':
            kwargs['queryset'] = Employee.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductionLog)
class ProductionLogAdmin(ModelAdmin):
    list_display = ['id', 'ticket', 'from_stage', 'to_stage', 'performed_by', 'timestamp']
    list_filter = ['to_stage', 'timestamp']
    search_fields = ['ticket__id', 'comments']

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
