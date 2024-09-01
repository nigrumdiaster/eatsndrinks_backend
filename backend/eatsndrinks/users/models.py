from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.


class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.first_name + self.last_name

    