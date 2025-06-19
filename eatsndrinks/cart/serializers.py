from rest_framework import serializers
from .models import Cart, CartItem
from catalogue.models import Product  # Import Product model
from drf_spectacular.utils import extend_schema_field
from decimal import Decimal

from rest_framework import serializers
from .models import Cart, CartItem
from catalogue.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_mainimage = serializers.ImageField(source='product.mainimage', use_url=True)
    product_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_mainimage", "product_price", "quantity"]

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_product_price(self, obj):
        product = obj.product
        try:
            return float(product.current_price())  # GỌI HÀM BẰNG ()
        except Exception as e:
            print(f"[DEBUG] Lỗi khi lấy giá sản phẩm: {e}")
            return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items"]
        extra_kwargs = {"user": {"read_only": True}}  # User field is read-only

class CartItemQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]  # Chỉ lấy trường quantity