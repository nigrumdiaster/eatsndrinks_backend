from django.db import models
from accounts.models import Account
from products.models import Product

class Cart(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Giỏ Hàng"
        verbose_name_plural = "Giỏ Hàng"
    
    def __str__(self):
        return f"MKH: {self.account.id} - Tên Sản Phẩm: {self.product.name if self.product else 'N/A'}"
