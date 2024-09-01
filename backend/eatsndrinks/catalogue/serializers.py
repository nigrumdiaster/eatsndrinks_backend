from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["pk", "name", "description", "is_active"]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["pk", "name", "description", "mainimage", "is_active", "quantity", "price", "category", "created_at", "updated_at"]
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

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']

    def validate_product(self, value):
        if not Product.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Sản phẩm không tồn tại.")
        return value
    
    def validate_image(self, value):
        # Kiểm tra định dạng tệp
        if not value.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError("Chỉ hỗ trợ các định dạng hình ảnh PNG, JPG, JPEG.")

        # Kiểm tra kích thước tệp (ví dụ: tối đa 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Kích thước tệp không được vượt quá 5MB.")

        return value
    
    def validate(self, data):
        if not data.get('product') and data.get('image'):
            raise serializers.ValidationError("Phải cung cấp sản phẩm khi gửi hình ảnh.")
        return data