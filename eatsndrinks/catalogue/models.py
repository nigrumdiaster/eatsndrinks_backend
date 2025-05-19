from django.db import models

# from taggit.managers import TaggableManager
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    mainimage = models.ImageField(upload_to="product_main_images/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    flash_sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    flash_sale_start = models.DateTimeField(null=True, blank=True)
    flash_sale_end = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name="products", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_flash_sale_active(self):
        now = timezone.now()
        return (
            self.flash_sale_start
            and self.flash_sale_end
            and self.flash_sale_start <= now <= self.flash_sale_end
        )

    def current_price(self):
        if self.is_flash_sale_active() and self.flash_sale_price:
            return self.flash_sale_price
        return self.price

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="product_images/", blank=True, null=True
    ) 

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"
