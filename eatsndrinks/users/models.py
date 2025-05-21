from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
# Create your models here.


class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^0[0-9]{9}$',
                message="Số điện thoại phải bắt đầu bằng 0 và theo sau là 9 chữ số.",
            )
        ]
    )
    address = models.TextField(blank=True, null=True)

    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.first_name + self.last_name