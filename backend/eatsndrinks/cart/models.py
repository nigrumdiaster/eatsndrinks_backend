from django.db import models
from users.models import User
from catalogue.models import Product

class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Giỏ Hàng"
        verbose_name_plural = "Giỏ Hàng"
    
    def __str__(self):
        return f"MKH: {self.user.id} - Tên Sản Phẩm: {self.product.name if self.product else 'N/A'}"
