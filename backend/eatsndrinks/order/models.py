from django.db import models
from catalogue.models import Product
from users.models import User
from django.core.validators import RegexValidator
class Order(models.Model):
    STATUS_CHOICES = (
        ("cxl", 'Chưa Xử Lý'),
        ("dxl", 'Đã Xử Lý'),
        ("dcbh", 'Đang Chuẩn Bị Hàng'),
        ("dgh", 'Đang Giao Hàng'),
        ("dghh", 'Đã Giao Hàng'),
        ("khh", 'Khách Hàng Hủy'),
        ("adh", 'Admin Hủy'),
        ("dtt", 'Đã thanh toán'),
    )
    PAYMENT_METHOD_CHOICES = (
        ("cod", 'Thanh toán khi giao hàng'),
        ("ppl", 'Thanh toán qua paypal')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    total_price = models.IntegerField()
    notes = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    payment_method = models.CharField(max_length=25, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_CHOICES[0][0])

    class Meta:
        verbose_name = "Đơn Hàng"
        verbose_name_plural = "Đơn Hàng"

    def __str__(self):
        return "Mã Đơn Hàng: " + str(self.id) + " - Khách Hàng: " + self.user.first_name + " " + self.user.last_name + " - Tổng Tiền: " + str(self.total_amount) + " - Thời Gian: " + self.created_at.strftime("%Y-%m-%d %H:%M:%S")

class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit_price = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    total_price = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Chi Tiết Đơn Hàng"
        verbose_name_plural = "Chi Tiết Đơn Hàng"

    def save(self, *args, **kwargs):
        self.unit_price = self.product.unit_price
        self.total_price = self.product.unit_price * self.quantity
        super(OrderDetail, self).save(*args, **kwargs)

    def __str__(self):
        return "Mã Đơn Hàng: " + str(self.order.id) + " - Sản Phẩm: " + self.product.name + " - Giá Bán: " + str(self.unit_price) + " - Số Lượng: " + str(self.quantity) + " - Tổng Tiền: " + str(self.total_price)
