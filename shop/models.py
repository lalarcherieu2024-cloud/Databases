from django.db import models


ORDER_STATUS_CHOICES = [
    ('received', 'Received'),
    ('confirmed', 'Confirmed'),
    ('in_production', 'In Production'),
    ('ready_for_delivery', 'Ready for Delivery'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

GARMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_production', 'In Production'),
    ('completed', 'Completed'),
    ('on_hold', 'On Hold'),
]

TICKET_STAGE_CHOICES = [
    ('order_received', 'Order Received'),
    ('design_confirmed', 'Design Confirmed'),
    ('cutting', 'Cutting'),
    ('sewing', 'Sewing'),
    ('finishing', 'Finishing'),
    ('quality_check', 'Quality Check'),
    ('ready_for_delivery', 'Ready for Delivery'),
    ('rework', 'Rework'),
]

PRIORITY_CHOICES = [
    ('normal', 'Normal'),
    ('urgent', 'Urgent'),
    ('rush', 'Rush'),
]

DELIVERY_METHOD_CHOICES = [
    ('pickup', 'Pickup at Shop'),
    ('courier', 'Courier'),
    ('in_person', 'In-Person Delivery'),
]


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Preferences or anything to remember about this customer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Material(models.Model):
    name = models.CharField(max_length=100)
    fabric_type = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    stock_meters = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_per_meter = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.color})" if self.color else self.name


class Measurement(models.Model):
    bust = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    waist = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    hips = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    shoulder_width = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sleeve_length = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    inseam = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    total_length = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    extra_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Measurement #{self.pk}"


class Garment(models.Model):
    garment_type = models.CharField(max_length=50, help_text="dress, suit, trousers, shirt, etc.")
    color = models.CharField(max_length=50, blank=True)
    design_notes = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=30, choices=GARMENT_STATUS_CHOICES, default='pending')
    measurement = models.OneToOneField(
        Measurement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='garment',
    )
    materials = models.ManyToManyField(Material, blank=True, related_name='garments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.garment_type} ({self.color})" if self.color else self.garment_type


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    order_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='received')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date', '-id']

    def __str__(self):
        return f"Order #{self.pk} - {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    garment = models.ForeignKey(Garment, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.garment} (Order #{self.order_id})"

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, help_text="tailor, seamstress, cutter, etc.")
    phone = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class WorkTicket(models.Model):
    garment = models.ForeignKey(Garment, on_delete=models.CASCADE, related_name='tickets')
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
    )
    current_stage = models.CharField(max_length=30, choices=TICKET_STAGE_CHOICES, default='order_received')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    deadline = models.DateField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.pk} - {self.garment}"


class ProductionLog(models.Model):
    ticket = models.ForeignKey(WorkTicket, on_delete=models.CASCADE, related_name='logs')
    performed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='production_logs',
    )
    from_stage = models.CharField(max_length=30, choices=TICKET_STAGE_CHOICES, blank=True)
    to_stage = models.CharField(max_length=30, choices=TICKET_STAGE_CHOICES)
    comments = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Log #{self.pk}: {self.from_stage} -> {self.to_stage}"


class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_date = models.DateField(null=True, blank=True)
    method = models.CharField(max_length=30, choices=DELIVERY_METHOD_CHOICES, default='pickup')
    final_observations = models.TextField(blank=True)
    recipient_name = models.CharField(max_length=200, blank=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Deliveries'

    def __str__(self):
        return f"Delivery for Order #{self.order_id}"

# Module E — Delivery
from shop.models_delivery import Delivery
