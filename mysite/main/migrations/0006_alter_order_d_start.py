# Generated by Django 5.1.1 on 2024-09-23 17:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_order_status_order_alter_order_d_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='d_start',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 23, 17, 12, 58, 206622, tzinfo=datetime.timezone.utc), verbose_name='Дата создания'),
        ),
    ]