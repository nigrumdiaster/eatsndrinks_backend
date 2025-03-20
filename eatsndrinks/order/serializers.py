from rest_framework import serializers
from .models import Order, OrderDetail
from cart.models import CartItem

class OrderDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderDetail
        fields = ["product", "product_name", "unit_price", "quantity", "total_price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(source="orderdetail_set", many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "user", "phone_number", "address", "total_price", "status", "payment_method", "payment_status", "created_at", "items"]
        extra_kwargs = {"user": {"read_only": True}, "total_price": {"read_only": True}, "status": {"read_only": True}}

    def create(self, validated_data):
        user = self.context["request"].user  # Get the current user
        cart_items = CartItem.objects.filter(cart__user=user)  # Get user's cart items

        if not cart_items.exists():
            raise serializers.ValidationError("Giỏ hàng của bạn đang trống!")

        # First, calculate the total price before creating the order
        total_price = 0
        for item in cart_items:
            total_price += item.product.price * item.quantity

        # Create the order with the calculated total_price
        order = Order.objects.create(user=user, total_price=total_price, **validated_data)

        # Create order details
        for item in cart_items:
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                unit_price=item.product.price,
                quantity=item.quantity,
                total_price=item.product.price * item.quantity
            )

        # Clear the user's cart after placing an order
        cart_items.delete()

        return order
