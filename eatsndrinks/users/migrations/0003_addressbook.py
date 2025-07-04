# Generated by Django 5.1 on 2025-06-12 10:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_date_of_birth'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField()),
                ('is_default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='address_book', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
