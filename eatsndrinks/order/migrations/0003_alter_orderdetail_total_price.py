# Generated by Django 5.1 on 2025-03-10 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_order_address_order_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='total_price',
            field=models.IntegerField(default=0),
        ),
    ]
