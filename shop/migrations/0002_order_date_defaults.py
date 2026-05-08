from django.db import migrations, models

import shop.models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_date",
            field=models.DateField(default=shop.models.today, help_text="Must be today's date."),
        ),
        migrations.AlterField(
            model_name="order",
            name="due_date",
            field=models.DateField(
                default=shop.models.tomorrow,
                help_text="Defaults to tomorrow; must be after the order date.",
            ),
        ),
        migrations.AlterField(
            model_name="workticket",
            name="assigned_to",
            field=models.ForeignKey(
                blank=True,
                help_text="Pick an active employee whose role/specialization matches the current stage.",
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="tickets",
                to="shop.employee",
            ),
        ),
    ]
