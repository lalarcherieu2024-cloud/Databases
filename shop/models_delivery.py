"""
Module E — Delivery Model
Owns: Delivery entity
Workflow contribution: Workflow 3 Steps 4–6

This file defines the Delivery model. It should be imported
into the main models.py or registered via the app's __init__.

To integrate: add the following import to shop/models.py:
    from shop.models_delivery import Delivery
Or copy the Delivery class directly into shop/models.py.
"""

from django.db import models
from django.core.exceptions import ValidationError


class Delivery(models.Model):
    """
    Tracks the delivery or pickup of a completed order.
    One-to-one relationship with Order (each order can have
    at most one delivery record).

    Business rules:
    - A delivery can only be created for orders with status
      'ready_for_delivery' or later.
    - Once confirmed=True, the associated order status should
      be updated to 'delivered'.
    - delivery_date is required when confirmed is True.
    """

    METHOD_CHOICES = [
        ('pickup', 'Pickup at Shop'),
        ('courier', 'Courier Delivery'),
        ('in_person', 'In-Person Delivery'),
    ]

    order = models.OneToOneField(
        'Order',
        on_delete=models.CASCADE,
        related_name='delivery',
        help_text='The order this delivery is associated with.',
    )
    delivery_date = models.DateField(
        null=True,
        blank=True,
        help_text='Actual date of delivery or pickup.',
    )
    method = models.CharField(
        max_length=30,
        choices=METHOD_CHOICES,
        default='pickup',
        help_text='How the order will be delivered to the customer.',
    )
    final_observations = models.TextField(
        blank=True,
        default='',
        help_text='Any final notes, issues, or observations about the delivery.',
    )
    recipient_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Name of the person who receives the order.',
    )
    confirmed = models.BooleanField(
        default=False,
        help_text='Whether the customer has confirmed receipt of the order.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']

    def __str__(self):
        status = 'Confirmed' if self.confirmed else 'Pending'
        return f'Delivery #{self.pk} — Order #{self.order_id} ({status})'

    def clean(self):
        """Validate business rules before saving."""
        super().clean()
        # Rule: if confirmed, delivery_date is required
        if self.confirmed and not self.delivery_date:
            raise ValidationError({
                'delivery_date': 'Delivery date is required when confirming delivery.',
            })

    def confirm_delivery(self):
        """
        Mark this delivery as confirmed and update the
        associated order status to 'delivered'.
        Workflow 3, Step 5–6.
        """
        from django.utils import timezone
        if not self.delivery_date:
            self.delivery_date = timezone.now().date()
        self.confirmed = True
        self.full_clean()
        self.save()

        # Update the order status
        order = self.order
        order.status = 'delivered'
        order.save(update_fields=['status', 'updated_at'])
