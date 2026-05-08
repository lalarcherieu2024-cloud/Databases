"""
Costuras de Paqui - Admin Configuration
"""

from django.contrib import admin, messages
from django.db.models import Q
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from django import forms
from .models import (
    Customer,
    Order, OrderItem,
    Garment, Measurement, Material,
    Employee, WorkTicket, ProductionLog,
    Delivery,
    STAGE_SPECIALIZATION_KEYWORDS,
    TICKET_STAGE_ORDER,
)


def _next_stage(current):
    try:
        idx = TICKET_STAGE_ORDER.index(current)
    except ValueError:
        return None
    if idx + 1 >= len(TICKET_STAGE_ORDER):
        return None
    return TICKET_STAGE_ORDER[idx + 1]


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

    @display(
    description="Status",
    ordering="status",
    label={
        "received": "info",
        "confirmed": "info",
        "in_production": "warning",
        "ready_for_delivery": "success",
        "delivered": "success",
        "cancelled": "danger",
    },
)
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @admin.action(description="Mark selected orders as confirmed")
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status="confirmed")
        self.message_user(request, f"{updated} order(s) marked as confirmed.")


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ["id", "order", "garment", "quantity", "unit_price_display", "line_total_display"]
    search_fields = ["order__id", "garment__garment_type"]

    @display(description="Unit price", ordering="unit_price")
    def unit_price_display(self, obj):
        return f"€{obj.unit_price:,.2f}"

    @display(description="Line total")
    def line_total_display(self, obj):
        return f"€{obj.line_total:,.2f}"



class GarmentForm(forms.ModelForm):
    """
    Custom form for Garment that exposes Measurement fields inline.
    Saves changes back to the related Measurement (creating one if needed).
    """
    bust = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
    waist = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
    hips = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
    shoulder_width = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
    sleeve_length = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
    inseam = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
    total_length = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
    extra_notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    class Meta:
        model = Garment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill measurement fields from the linked Measurement, if any
        if self.instance and self.instance.pk and self.instance.measurement:
            m = self.instance.measurement
            self.fields["bust"].initial = m.bust
            self.fields["waist"].initial = m.waist
            self.fields["hips"].initial = m.hips
            self.fields["shoulder_width"].initial = m.shoulder_width
            self.fields["sleeve_length"].initial = m.sleeve_length
            self.fields["inseam"].initial = m.inseam
            self.fields["total_length"].initial = m.total_length
            self.fields["extra_notes"].initial = m.extra_notes

    def save(self, commit=True):
        garment = super().save(commit=False)

        # Get or create the linked Measurement
        if garment.measurement:
            m = garment.measurement
        else:
            m = Measurement.objects.create()
            garment.measurement = m

        # Push form values into the Measurement
        m.bust = self.cleaned_data.get("bust")
        m.waist = self.cleaned_data.get("waist")
        m.hips = self.cleaned_data.get("hips")
        m.shoulder_width = self.cleaned_data.get("shoulder_width")
        m.sleeve_length = self.cleaned_data.get("sleeve_length")
        m.inseam = self.cleaned_data.get("inseam")
        m.total_length = self.cleaned_data.get("total_length")
        m.extra_notes = self.cleaned_data.get("extra_notes") or ""
        m.save()

        if commit:
            garment.save()
            self.save_m2m()
        return garment


@admin.register(Garment)
class GarmentAdmin(ModelAdmin):
    form = GarmentForm
    list_display = ["id", "garment_type", "color", "priority_badge", "status_badge", "created_at"]
    list_filter = ["status", "priority", "garment_type"]
    search_fields = ["garment_type", "color"]
    filter_horizontal = ["materials"]

    fieldsets = (
        ("Garment details", {
            "fields": ("garment_type", "color", "design_notes", "priority", "status", "materials"),
        }),
        ("📏 Measurements", {
            "fields": (
                ("bust", "waist", "hips"),
                ("shoulder_width", "sleeve_length"),
                ("inseam", "total_length"),
                "extra_notes",
            ),
            "classes": ("collapse",),  # collapsible section, opens on click
        }),
    )

    @display(
        description="Status",
        ordering="status",
        label={
            "pending": "info",
            "in_production": "warning",
            "completed": "success",
            "on_hold": "danger",
        },
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @display(
        description="Priority",
        ordering="priority",
        label={
            "normal": "info",
            "urgent": "warning",
            "rush": "danger",
        },
    )
    def priority_badge(self, obj):
        return obj.priority, obj.get_priority_display()
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
        new_stage = _next_stage(ticket.current_stage)
        if new_stage is None:
            skipped += 1
            continue
        ticket.current_stage = new_stage
        # WorkTicket.save() writes the ProductionLog automatically and,
        # when reaching "ready_for_delivery", auto-creates the Delivery.
        ticket.save()
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
        ticket.current_stage = "rework"
        ticket.save()
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

    @display(
    description="Stage",
    ordering="current_stage",
    label={
        "order_received": "info",
        "design_confirmed": "info",
        "cutting": "warning",
        "sewing": "warning",
        "finishing": "warning",
        "quality_check": "warning",
        "ready_for_delivery": "success",
        "rework": "danger",
    },
)
    def stage_badge(self, obj):
        return obj.current_stage, obj.get_current_stage_display()

    @display(
        description="Priority",
        ordering="priority",
        label={
            "normal": "info",
            "urgent": "warning",
            "rush": "danger",
        },
    )
    def priority_badge(self, obj):
        return obj.priority, obj.get_priority_display()

    def get_form(self, request, obj=None, **kwargs):
        request._workticket_obj = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            qs = Employee.objects.filter(is_active=True)
            obj = getattr(request, "_workticket_obj", None)
            stage = obj.current_stage if obj else "order_received"
            keywords = STAGE_SPECIALIZATION_KEYWORDS.get(stage, [])
            if keywords:
                q = Q()
                for kw in keywords:
                    q |= Q(role__icontains=kw) | Q(specialization__icontains=kw)
                qs = qs.filter(q)
            kwargs["queryset"] = qs.distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ProductionLog)
class ProductionLogAdmin(ModelAdmin):
    list_display = ["id", "ticket", "from_stage_badge", "to_stage_badge", "performed_by", "timestamp"]
    list_filter = ["to_stage", "timestamp"]
    search_fields = ["ticket__id", "comments"]

    @display(
        description="From",
        ordering="from_stage",
        label={
            "order_received": "info",
            "design_confirmed": "info",
            "cutting": "warning",
            "sewing": "warning",
            "finishing": "warning",
            "quality_check": "warning",
            "ready_for_delivery": "success",
            "rework": "danger",
        },
    )
    def from_stage_badge(self, obj):
        if not obj.from_stage:
            return None, "—"
        return obj.from_stage, obj.get_from_stage_display()

    @display(
        description="To",
        ordering="to_stage",
        label={
            "order_received": "info",
            "design_confirmed": "info",
            "cutting": "warning",
            "sewing": "warning",
            "finishing": "warning",
            "quality_check": "warning",
            "ready_for_delivery": "success",
            "rework": "danger",
        },
    )
    def to_stage_badge(self, obj):
        return obj.to_stage, obj.get_to_stage_display()

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
    list_display = ["order", "delivery_date", "method", "recipient_name", "confirmed_badge"]
    list_filter = ["method", "confirmed", "delivery_date"]
    search_fields = ["order__id", "recipient_name"]
    autocomplete_fields = ["order"]

    @display(
        description="Status",
        ordering="confirmed",
        label={
            True: "success",
            False: "warning",
        },
    )
    def confirmed_badge(self, obj):
        if obj.confirmed:
            return True, "Confirmed"
        return False, "Pending"