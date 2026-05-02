import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_id', models.IntegerField(db_index=True)),
                ('product_id', models.IntegerField(db_index=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='posts_images/')),
                ('category', models.CharField(db_index=True, max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(db_index=True)),
                ('stars', models.PositiveSmallIntegerField()),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviews',
                    to='social.post',
                )),
            ],
            options={'unique_together': {('post', 'user_id')}},
        ),
        migrations.CreateModel(
            name='UserRef',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=150)),
                ('role', models.CharField(max_length=20)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='StoreRef',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('seller_id', models.IntegerField(db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('wilaya', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('rating', models.FloatField(default=0.0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductRef',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('store_id', models.IntegerField(db_index=True)),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.CharField(default='General', max_length=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
