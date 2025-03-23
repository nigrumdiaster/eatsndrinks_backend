# Generated by Django 5.1 on 2025-03-22 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_order_payment_status_alter_order_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('cxl', 'Chưa Xử Lý'), ('dcbh', 'Đang Chuẩn Bị Hàng'), ('dgh', 'Đang Giao Hàng'), ('dghh', 'Đã Giao Hàng'), ('khh', 'Khách Hàng Hủy'), ('adh', 'Admin Hủy')], default='cxl', max_length=25),
        ),
    ]
