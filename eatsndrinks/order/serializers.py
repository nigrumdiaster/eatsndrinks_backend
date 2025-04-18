from rest_framework import serializers
from .models import Order, OrderDetail
from cart.models import CartItem

class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_image = serializers.ImageField(source="product.mainimage", read_only=True)

    class Meta:
        model = OrderDetail
        fields = ["product", "product_name", "product_image", "unit_price", "quantity", "total_price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(source="orderdetail_set", many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "phone_number", "address", "total_price", "status", "payment_method", "payment_status", "created_at", "items"]
        extra_kwargs = {"user": {"read_only": True}, "total_price": {"read_only": True}, "status": {"read_only": True}, "payment_status": {"read_only": True}}

    def create(self, validated_data):
        user = self.context["request"].user  # Get the current user
        cart_items = CartItem.objects.filter(cart__user=user)  # Get user's cart items

        if not cart_items.exists():
            raise serializers.ValidationError("Giỏ hàng của bạn đang trống!")

        # First, calculate the total price before creating the order
        total_price = 0
        for item in cart_items:
            # Lấy giá đúng của sản phẩm theo flash sale nếu có
            if item.product.is_flash_sale_active() and item.product.flash_sale_price:
                unit_price = item.product.flash_sale_price
            else:
                unit_price = item.product.price

            total_price += unit_price * item.quantity

        # Create the order with the calculated total_price
        order = Order.objects.create(user=user, total_price=total_price, **validated_data)

        # Create order details
        for item in cart_items:
            # Lấy giá đúng của sản phẩm theo flash sale nếu có
            if item.product.is_flash_sale_active() and item.product.flash_sale_price:
                unit_price = item.product.flash_sale_price
            else:
                unit_price = item.product.price

            # Create order detail with correct unit price and total price
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                unit_price=unit_price,
                quantity=item.quantity,
                total_price=unit_price * item.quantity
            )

        # Clear the user's cart after placing an order
        cart_items.delete()

        return order

class AdminOrderSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(source="orderdetail_set", many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            "id", "user", "phone_number", "address", "total_price", 
            "status", "payment_method", "payment_status", "created_at", "items"
        ]
        extra_kwargs = {
            "user": {"read_only": True},  # Admin không thay đổi user
            "total_price": {"read_only": True},  # Không thay đổi tổng tiền
            "created_at": {"read_only": True}  # Không thay đổi thời gian tạo
        }

    def update(self, instance, validated_data):
        """Cho phép admin cập nhật trạng thái & thanh toán"""
        instance.status = validated_data.get("status", instance.status)
        instance.payment_status = validated_data.get("payment_status", instance.payment_status)
        instance.save()
        return instance