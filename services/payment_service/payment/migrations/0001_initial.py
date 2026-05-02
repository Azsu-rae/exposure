import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.UUIDField(unique=True)),
                ('seller_id', models.IntegerField()),
                ('buyer_id', models.IntegerField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('method', models.CharField(choices=[('CASH', 'Cash'), ('CARD', 'Card')], max_length=10)),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pending'),
                        ('HELD', 'Held'),
                        ('RELEASED', 'Released'),
                        ('REFUNDED', 'Refunded'),
                        ('FAILED', 'Failed'),
                    ],
                    default='PENDING',
                    max_length=10,
                )),
                ('checkout_url', models.URLField(blank=True, null=True)),
                ('release_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
