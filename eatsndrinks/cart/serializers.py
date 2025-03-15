from rest_framework import serializers
from .models import Cart, CartItem
from catalogue.models import Product  # Import Product model

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')  # Display product name
    product_mainimage = serializers.ImageField(source='product.mainimage', use_url=True)
    product_price = serializers.IntegerField(source='product.price', read_only=True)
    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_mainimage", "product_price", "quantity"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items"]
        extra_kwargs = {"user": {"read_only": True}}  # User field is read-only
