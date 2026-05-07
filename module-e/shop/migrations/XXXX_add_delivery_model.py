"""
Migration for the Delivery model — Module E.

NOTE: This is a TEMPLATE migration. After integrating the model
into your project, run:
    python manage.py makemigrations shop
    python manage.py migrate

to generate the actual migration. This file shows the expected
schema for reference.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # Update this to match the latest migration in your shop app
        # e.g., ('shop', '0004_auto_xxxxx'),
        ('shop', '__latest__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_date', models.DateField(blank=True, help_text='Actual date of delivery or pickup.', null=True)),
                ('method', models.CharField(choices=[('pickup', 'Pickup at Shop'), ('courier', 'Courier Delivery'), ('in_person', 'In-Person Delivery')], default='pickup', help_text='How the order will be delivered to the customer.', max_length=30)),
                ('final_observations', models.TextField(blank=True, default='', help_text='Any final notes, issues, or observations about the delivery.')),
                ('recipient_name', models.CharField(blank=True, default='', help_text='Name of the person who receives the order.', max_length=200)),
                ('confirmed', models.BooleanField(default=False, help_text='Whether the customer has confirmed receipt of the order.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(help_text='The order this delivery is associated with.', on_delete=django.db.models.deletion.CASCADE, related_name='delivery', to='shop.order')),
            ],
            options={
                'verbose_name': 'Delivery',
                'verbose_name_plural': 'Deliveries',
                'ordering': ['-created_at'],
            },
        ),
    ]
