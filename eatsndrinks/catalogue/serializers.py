from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Category, Product, ProductImage, ProductCombo, ProductComboItem


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
        if not hasattr(value, "name") or not value.name.lower().endswith(
            valid_extensions
        ):
            raise ValidationError("Chỉ hỗ trợ các định dạng hình ảnh PNG, JPG, JPEG.")

        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise ValidationError("Kích thước tệp không được vượt quá 5MB.")

        return value


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    is_flash_sale_active = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "mainimage",
            "price",
            "flash_sale_price",
            "flash_sale_start",
            "flash_sale_end",
            "category",
            "is_active",
            "created_at",
            "updated_at",
            "images",
            "is_flash_sale_active",
            "current_price",
            "uploaded_images",
        ]

    def get_is_flash_sale_active(self, obj):
        return obj.is_flash_sale_active()

    def get_current_price(self, obj):
        return obj.current_price()

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Giá không thể âm.")
        return value

    def create(self, validated_data):
        uploaded_images = validated_data.pop(
            "uploaded_images", []
        )  # Lấy danh sách ảnh tải lên
        product = Product.objects.create(**validated_data)  # Tạo sản phẩm mới

        # Lưu ảnh vào ProductImage
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        # Loại bỏ các trường read-only trước khi cập nhật
        validated_data.pop("created_at", None)
        validated_data.pop("updated_at", None)

        uploaded_images = validated_data.pop("uploaded_images", [])

        # Cập nhật các trường còn lại của sản phẩm
        instance = super().update(instance, validated_data)

        if uploaded_images:
            # 🔥 XÓA TẤT CẢ ẢNH CŨ
            instance.images.all().delete()

            # 📤 THÊM ẢNH MỚI
            for image in uploaded_images:
                ProductImage.objects.create(product=instance, image=image)

        return instance


class ProductComboItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductComboItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity']


class ProductComboSerializer(serializers.ModelSerializer):
    items = ProductComboItemSerializer(many=True, read_only=True)
    total_original_price = serializers.SerializerMethodField()
    total_discounted_price = serializers.SerializerMethodField()
    combo_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="Danh sách sản phẩm trong combo. Format: [{'product': id, 'quantity': số lượng}]"
    )

    class Meta:
        model = ProductCombo
        fields = [
            'id', 'name', 'description', 'discount_amount',
            'is_active', 'created_at', 'updated_at',
            'items', 'total_original_price', 'total_discounted_price',
            'combo_items'
        ]

    def get_total_original_price(self, obj):
        total = sum(
            item.product.price * item.quantity
            for item in obj.items.all()
        )
        return total

    def get_total_discounted_price(self, obj):
        original_price = self.get_total_original_price(obj)
        return max(0, original_price - obj.discount_amount)

    def create(self, validated_data):
        combo_items = validated_data.pop('combo_items', [])
        combo = ProductCombo.objects.create(**validated_data)
        
        # Tạo các items cho combo
        for item_data in combo_items:
            ProductComboItem.objects.create(
                combo=combo,
                product_id=item_data['product'],
                quantity=item_data['quantity']
            )
        
        return combo

    def update(self, instance, validated_data):
        combo_items = validated_data.pop('combo_items', None)
        instance = super().update(instance, validated_data)
        
        # Nếu có combo_items trong request, cập nhật lại toàn bộ items
        if combo_items is not None:
            # Xóa tất cả items cũ
            instance.items.all().delete()
            # Tạo items mới
            for item_data in combo_items:
                ProductComboItem.objects.create(
                    combo=instance,
                    product_id=item_data['product'],
                    quantity=item_data['quantity']
                )
        
        return instance
