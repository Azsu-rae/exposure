from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='moderation_status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pending'),
                    ('APPROVED', 'Approved'),
                    ('REJECTED', 'Rejected'),
                ],
                default='PENDING',
                db_index=True,
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='post',
            name='moderation_reason',
            field=models.TextField(blank=True),
        ),
    ]
