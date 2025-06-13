from rest_framework import serializers
from .models import Order, OrderDetail
from cart.models import CartItem
from catalogue.models import ProductCombo

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
        extra_kwargs = {"user": {"read_only": True}, "total_price": {"read_only": True}, "status": {"read_only": True}}

    def create(self, validated_data):
        user = self.context["request"].user
        cart_items = CartItem.objects.filter(cart__user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("Giỏ hàng của bạn đang trống!")

        # Tính toán tổng tiền và kiểm tra combo
        total_price = 0
        applied_combos = set()  # Theo dõi các combo đã áp dụng

        # Lấy tất cả combo đang active
        active_combos = ProductCombo.objects.filter(is_active=True)

        # Tạo order với giá ban đầu
        order = Order.objects.create(user=user, total_price=0, **validated_data)

        # Xử lý từng item trong giỏ hàng
        for item in cart_items:
            # Lấy giá sản phẩm (có flash sale không)
            if item.product.is_flash_sale_active() and item.product.flash_sale_price:
                unit_price = item.product.flash_sale_price
            else:
                unit_price = item.product.price

            # Kiểm tra xem sản phẩm có thuộc combo nào không
            item_in_combo = False
            for combo in active_combos:
                if combo.id in applied_combos:
                    continue  # Bỏ qua combo đã áp dụng

                combo_items = combo.items.all()
                # Kiểm tra xem tất cả sản phẩm trong combo có trong giỏ hàng không
                combo_products = {ci.product: ci.quantity for ci in combo_items}
                cart_products = {item.product: item.quantity for item in cart_items}

                # Kiểm tra số lượng sản phẩm trong combo có đủ không
                if all(
                    product in cart_products and cart_products[product] >= quantity
                    for product, quantity in combo_products.items()
                ):
                    # Áp dụng giảm giá combo
                    total_price += (unit_price * item.quantity) - combo.discount_amount
                    applied_combos.add(combo.id)
                    item_in_combo = True
                    break

            if not item_in_combo:
                total_price += unit_price * item.quantity

            # Tạo order detail
            OrderDetail.objects.create(
                order=order,
                product=item.product,
                unit_price=unit_price,
                quantity=item.quantity,
                total_price=unit_price * item.quantity
            )

        # Cập nhật tổng tiền của order
        order.total_price = total_price
        order.save()

        # Xóa giỏ hàng sau khi đặt hàng
        cart_items.delete()

        return order

class AdminOrderSerializer(serializers.ModelSerializer):
    items = OrderDetailSerializer(source="orderdetail_set", many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "user", "full_name", "phone_number", "address", "total_price", 
            "status", "payment_method", "payment_status", "created_at", "items"
        ]
        extra_kwargs = {
            "user": {"read_only": True},  # Admin không thay đổi user
            "total_price": {"read_only": True},  # Không thay đổi tổng tiền
            "created_at": {"read_only": True}  # Không thay đổi thời gian tạo
        }

    def get_full_name(self, obj):
        # Lấy họ và tên từ user
        return f"{obj.user.first_name} {obj.user.last_name}"

    def update(self, instance, validated_data):
        """Cho phép admin cập nhật trạng thái & thanh toán"""
        instance.status = validated_data.get("status", instance.status)
        instance.payment_status = validated_data.get("payment_status", instance.payment_status)
        instance.save()
        return instance

class RecentCustomerSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        model = Order
        fields = ["customer_name", "customer_phone", "total_price"]

    def get_customer_name(self, obj):
        # Lấy tên đầy đủ từ first_name và last_name
        return f"{obj.user.first_name} {obj.user.last_name}"