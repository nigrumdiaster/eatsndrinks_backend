from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Category, Product, ProductImage


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "is_active"]


# Product Image Serializer
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "product"]

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


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)  
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )  # Cho phép upload nhiều ảnh cùng lúc
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "mainimage", "is_active",
            "quantity", "price", "category", "category_name",  
            "created_at", "updated_at", "images", "uploaded_images"  # Thêm uploaded_images
        ]
        read_only_fields = ["created_at", "updated_at", "category_name"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Giá không thể âm.")
        return value

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])  # Lấy danh sách ảnh tải lên
        product = Product.objects.create(**validated_data)  # Tạo sản phẩm mới

        # Lưu ảnh vào ProductImage
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        # Loại bỏ các trường read-only trước khi cập nhật
        validated_data.pop('created_at', None)
        validated_data.pop('updated_at', None)

        uploaded_images = validated_data.pop("uploaded_images", [])  # Lấy danh sách ảnh mới (nếu có)
        
        instance = super().update(instance, validated_data)  # Cập nhật sản phẩm

        # Nếu có ảnh mới, thêm vào product
        if uploaded_images:
            for image in uploaded_images:
                ProductImage.objects.create(product=instance, image=image)

        return instance
