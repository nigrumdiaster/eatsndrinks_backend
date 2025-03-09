from rest_framework import serializers
from .models import Category, Product, ProductImage
from django.core.exceptions import ValidationError

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["pk", "name", "description", "is_active"]

# Product Image Serializer
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product']  # Add 'product' field if needed

    def validate_image(self, value):
        # Allowed extensions
        valid_extensions = (".png", ".jpg", ".jpeg")
        
        # Check file extension
        if not hasattr(value, "name") or not value.name.lower().endswith(valid_extensions):
            raise ValidationError("Chỉ hỗ trợ các định dạng hình ảnh PNG, JPG, JPEG.")

        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise ValidationError("Kích thước tệp không được vượt quá 5MB.")

        return value

    def validate(self, data):
        if not data.get('product') and data.get('image'):
            raise serializers.ValidationError("Phải cung cấp sản phẩm khi gửi hình ảnh.")
        return data

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)  # Link images to product

    class Meta:
        model = Product
        fields = ["pk", "name", "description", "mainimage", "is_active", "quantity", "price", "category", "created_at", "updated_at", "images"]
        read_only_fields = ["created_at", "updated_at"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Giá không thể âm.")
        return value
    
    def update(self, instance, validated_data):
        # Loại bỏ các trường read-only trước khi cập nhật
        validated_data.pop('created_at', None)
        validated_data.pop('updated_at', None)
        return super().update(instance, validated_data)
