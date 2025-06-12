from django.db import models
from users.models import User
from catalogue.models import Product

class Cart(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Giỏ Hàng"
        verbose_name_plural = "Giỏ Hàng"
    
    def __str__(self):
        return f"MKH: {self.user.id} - MGH: {self.id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Sản Phẩm Trong Giỏ Hàng"
        verbose_name_plural = "Sản Phẩm Trong Giỏ Hàng"
    
    def __str__(self):
        return f"MGH: {self.cart.id} - Tên Sản Phẩm: {self.product.name if self.product else 'N/A'}"