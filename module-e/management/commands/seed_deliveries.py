"""
Management command to seed demo Delivery data.
Usage: python manage.py seed_deliveries

Creates sample delivery records for existing orders
that have status 'ready_for_delivery' or 'delivered'.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from shop.models import Order
from shop.models_delivery import Delivery


class Command(BaseCommand):
    help = 'Seed demo Delivery records for testing'

    def handle(self, *args, **options):
        methods = ['pickup', 'courier', 'in_person']
        observations = [
            'Customer was very satisfied with the final result.',
            'Minor delay due to courier availability.',
            'All garments inspected and approved before handover.',
            'Customer picked up in person, no issues.',
            'Delivered to front desk, confirmed by phone.',
            '',
        ]
        names = [
            'María García', 'Juan López', 'Ana Martínez',
            'Carlos Rodríguez', 'Lucía Hernández',
        ]

        # Find orders eligible for delivery
        eligible = Order.objects.filter(
            status__in=['ready_for_delivery', 'delivered']
        ).exclude(delivery__isnull=False)

        if not eligible.exists():
            self.stdout.write(self.style.WARNING(
                'No eligible orders found. Make sure there are orders '
                'with status "ready_for_delivery" or "delivered" '
                'that don\'t already have delivery records.'
            ))
            return

        created = 0
        for order in eligible:
            is_confirmed = order.status == 'delivered'
            d_date = (
                timezone.now().date() - timedelta(days=random.randint(1, 14))
                if is_confirmed
                else None
            )

            Delivery.objects.create(
                order=order,
                delivery_date=d_date,
                method=random.choice(methods),
                final_observations=random.choice(observations),
                recipient_name=random.choice(names),
                confirmed=is_confirmed,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {created} delivery record(s).'
        ))
