"""
Make Delivery rows creatable without an assigned driver/company so the
order.created consumer can persist a row immediately. Also fixes the
order_id type mismatch (the model declared UUIDField but the initial
migration created an IntegerField).
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='order_id',
            field=models.UUIDField(unique=True),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='driver',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='delivery.driver',
            ),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='company',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='delivery.deliverycompany',
            ),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='delivery_arrival_address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='delivery',
            name='estimated_delivery_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
