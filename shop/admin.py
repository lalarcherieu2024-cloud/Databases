"""
Costuras de Paqui - Admin Configuration
"""

from django.contrib import admin, messages
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import (
    Customer,
    Order, OrderItem,
    Garment, Measurement, Material,
    Employee, WorkTicket, ProductionLog,
    Delivery,
)


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ("full_name", "phone", "email", "created_at")
    search_fields = ("first_name", "last_name", "phone", "email")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

    @display(description="Full name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ["garment"]


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["id", "customer", "order_date", "due_date", "status_badge", "items_display", "total_price_display"]
    list_filter = ["status", "due_date", "order_date"]
    search_fields = ["customer__first_name", "customer__last_name", "id"]
    inlines = [OrderItemInline]
    autocomplete_fields = ["customer"]
    actions = ["mark_as_confirmed"]

    @display(description="Items")
    def items_display(self, obj):
        count = obj.items.count()
        return f"{count} item{'s' if count != 1 else ''}"

    @display(description="Total", ordering="total_price")
    def total_price_display(self, obj):
        return f"€{obj.total_price:,.2f}"

    @display(description="Status", ordering="status")
    def status_badge(self, obj):
        return obj.get_status_display()

    @admin.action(description="Mark selected orders as confirmed")
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status="confirmed")
        self.message_user(request, f"{updated} order(s) marked as confirmed.")


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ["id", "order", "garment", "quantity", "unit_price"]
    search_fields = ["order__id", "garment__garment_type"]


@admin.register(Garment)
class GarmentAdmin(ModelAdmin):
    list_display = ["id", "garment_type", "color", "priority_badge", "status_badge", "created_at"]
    list_filter = ["status", "priority", "garment_type"]
    search_fields = ["garment_type", "color"]
    filter_horizontal = ["materials"]
    autocomplete_fields = ["measurement"]

    @display(description="Status", ordering="status")
    def status_badge(self, obj):
        return obj.get_status_display()

    @display(description="Priority", ordering="priority")
    def priority_badge(self, obj):
        return obj.get_priority_display()


@admin.register(Measurement)
class MeasurementAdmin(ModelAdmin):
    list_display = ["id", "bust", "waist", "hips", "total_length"]
    search_fields = ["extra_notes"]


@admin.register(Material)
class MaterialAdmin(ModelAdmin):
    list_display = ["name", "fabric_type", "color", "stock_meters", "low_stock", "price_per_meter"]
    list_filter = ["fabric_type"]
    search_fields = ["name", "color"]

    @admin.display(boolean=True, description="Low stock (< 5m)")
    def low_stock(self, obj):
        return obj.stock_meters < 5


STAGE_ORDER = [
    "order_received",
    "design_confirmed",
    "cutting",
    "sewing",
    "finishing",
    "quality_check",
    "ready_for_delivery",
]


def _next_stage(current):
    try:
        index = STAGE_ORDER.index(current)
    except ValueError:
        return None

    next_index = index + 1
    if next_index < len(STAGE_ORDER):
        return STAGE_ORDER[next_index]
    return None


class ProductionLogInline(TabularInline):
    model = ProductionLog
    extra = 0
    fields = ["timestamp", "from_stage", "to_stage", "performed_by", "comments"]
    readonly_fields = ["timestamp", "from_stage", "to_stage", "performed_by", "comments"]
    can_delete = False
    ordering = ["-timestamp"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.action(description="Advance selected tickets to next stage")
def advance_to_next_stage(modeladmin, request, queryset):
    advanced = 0
    skipped = 0

    for ticket in queryset:
        old_stage = ticket.current_stage
        new_stage = _next_stage(old_stage)

        if new_stage is None:
            skipped += 1
            continue

        ticket.current_stage = new_stage
        ticket.save(update_fields=["current_stage", "updated_at"])

        ProductionLog.objects.create(
            ticket=ticket,
            performed_by=None,
            from_stage=old_stage,
            to_stage=new_stage,
            comments=f"Stage advanced via admin action: {old_stage} → {new_stage}",
        )

        advanced += 1

    if advanced:
        modeladmin.message_user(request, f"{advanced} ticket(s) advanced.", level=messages.SUCCESS)

    if skipped:
        modeladmin.message_user(request, f"{skipped} ticket(s) skipped.", level=messages.WARNING)


@admin.action(description="Send selected tickets to Rework")
def mark_as_rework(modeladmin, request, queryset):
    moved = 0

    for ticket in queryset:
        if ticket.current_stage == "rework":
            continue

        old_stage = ticket.current_stage
        ticket.current_stage = "rework"
        ticket.save(update_fields=["current_stage", "updated_at"])

        ProductionLog.objects.create(
            ticket=ticket,
            performed_by=None,
            from_stage=old_stage,
            to_stage="rework",
            comments=f"Sent to rework via admin action. Previous stage: {old_stage}.",
        )

        moved += 1

    modeladmin.message_user(request, f"{moved} ticket(s) moved to rework.", level=messages.SUCCESS)


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ["first_name", "last_name", "role", "specialization", "is_active"]
    list_filter = ["is_active", "role"]
    search_fields = ["first_name", "last_name", "role"]


@admin.register(WorkTicket)
class WorkTicketAdmin(ModelAdmin):
    list_display = ["id", "garment", "assigned_to", "stage_badge", "priority_badge", "deadline"]
    list_filter = ["current_stage", "priority"]
    search_fields = ["id", "garment__garment_type"]
    autocomplete_fields = ["garment", "assigned_to"]
    inlines = [ProductionLogInline]
    actions = [advance_to_next_stage, mark_as_rework]

    @display(description="Stage", ordering="current_stage")
    def stage_badge(self, obj):
        return obj.get_current_stage_display()

    @display(description="Priority", ordering="priority")
    def priority_badge(self, obj):
        return obj.get_priority_display()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = Employee.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductionLog)
class ProductionLogAdmin(ModelAdmin):
    list_display = ["id", "ticket", "from_stage_badge", "to_stage_badge", "performed_by", "timestamp"]
    list_filter = ["to_stage", "timestamp"]
    search_fields = ["ticket__id", "comments"]

    @display(description="From", ordering="from_stage")
    def from_stage_badge(self, obj):
        if not obj.from_stage:
            return "—"
        return obj.get_from_stage_display()

    @display(description="To", ordering="to_stage")
    def to_stage_badge(self, obj):
        return obj.get_to_stage_display()

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Delivery)
class DeliveryAdmin(ModelAdmin):
    list_display = ["order", "delivery_date", "method", "recipient_name", "confirmed"]
    list_filter = ["method", "confirmed", "delivery_date"]
    search_fields = ["order__id", "recipient_name"]
    autocomplete_fields = ["order"]