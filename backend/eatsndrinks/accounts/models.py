from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Account(models.Model):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default=MALE,
    )
    email = models.EmailField()
    slug = models.SlugField(
        blank=True, null=True, unique=True
    )  # Ensure slugs are unique

    class Meta:
        verbose_name = "Khách Hàng"
        verbose_name_plural = "Khách Hàng"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from user first name, last name, and user id
            self.slug = slugify(
                f"{self.user.first_name} {self.user.last_name} {self.user.id}"
            )
        super(Account, self).save(*args, **kwargs)

    def __str__(self):
        if not self.user.first_name and not self.user.last_name:
            return f"MKH: {self.user.id}"
        else:
            return f"MKH: {self.user.id}, Họ Tên: {self.user.first_name} {self.user.last_name}"
