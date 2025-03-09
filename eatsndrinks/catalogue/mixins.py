from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer
from rest_framework.response import Response
from rest_framework import status
class CustomPermissionMixin:
    def get_permissions(self):
        """
        Đặt quyền truy cập cho từng phương thức.
        """
        if self.request.method == 'GET':
            permission_classes = [AllowAny]  # Phân quyền cho phương thức GET
        elif self.request.method in ['POST', 'PUT', 'PATCH']:
            permission_classes = [IsAdminUser]  # Phân quyền cho phương thức POST, PUT, PATCH
        else:
            permission_classes = []  # Phân quyền cho các phương thức khác nếu cần

        return [permission() for permission in permission_classes]
    
class CategorySchemaMixin:
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Category.objects.all()
        else:
            return Category.objects.filter(is_active=True)

    @extend_schema(
        summary="Danh sách tất cả các danh mục",
        description="Lấy danh sách tất cả các danh mục có sẵn.",
        responses={200: CategorySerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Lấy thông tin một danh mục",
        description="Nhận thông tin chi tiết về một danh mục cụ thể.",
        responses={200: CategorySerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Tạo một danh mục mới",
        description="Tạo một danh mục mới với dữ liệu đã cung cấp.",
        request=CategorySerializer,
        responses={201: CategorySerializer},
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Danh mục mới đã được tạo thành công!", "data": response.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Cập nhật một danh mục",
        description="Cập nhật một danh mục hiện có với dữ liệu đã cung cấp.",
        request=CategorySerializer,
        responses={200: CategorySerializer},
    )
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {"message": "Danh mục đã được cập nhật thành công!", "data": response.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Cập nhật một phần của danh mục",
        description="Cập nhật một phần của danh mục hiện có với dữ liệu đã cung cấp.",
        request=CategorySerializer,
        responses={200: CategorySerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response(
            {"message": "Danh mục đã được cập nhật thành công!", "data": response.data},
            status=status.HTTP_200_OK,
        )

class ProductSchemaMixin:
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Product.objects.all()
        else:
            return Product.objects.filter(is_active=True, category__is_active=True)

    @extend_schema(
        summary='Danh sách tất cả các sản phẩm',
        description='Lấy danh sách tất cả các sản phẩm có sẵn.',
        responses={200: ProductSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Lấy thông tin một sản phẩm',
        description='Nhận thông tin chi tiết về một sản phẩm cụ thể.',
        responses={200: ProductSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary='Tạo một sản phẩm mới',
        description='Tạo một sản phẩm mới với dữ liệu đã cung cấp.',
        request=ProductSerializer,
        responses={201: ProductSerializer},
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Sản phẩm mới đã được tạo thành công!", "data": response.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary='Cập nhật một sản phẩm',
        description='Cập nhật một sản phẩm hiện có với dữ liệu đã cung cấp.',
        request=ProductSerializer,
        responses={200: ProductSerializer},
    )
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {"message": "Sản phẩm đã được cập nhật thành công!", "data": response.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary='Cập nhật một phần của sản phẩm',
        description='Cập nhật một phần của sản phẩm hiện có với dữ liệu đã cung cấp.',
        request=ProductSerializer,
        responses={200: ProductSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response(
            {"message": "Sản phẩm đã được cập nhật thành công!", "data": response.data},
            status=status.HTTP_200_OK,
        )

class ProductImageSchemaMixin:

    def get_queryset(self):
        if self.request.user.is_staff:
            return ProductImage.objects.all()
        else:
            return ProductImage.objects.filter(product__is_active=True)
    
    @extend_schema(
        summary='Danh sách tất cả các ảnh',
        description='Lấy danh sách tất cả các ảnh sản phẩm có sẵn.',
        responses={200: ProductImageSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Lấy thông tin một ảnh sản phẩm',
        description='Nhận thông tin chi tiết về một ảnh sản phẩm cụ thể.',
        responses={200: ProductImageSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary='Tạo một ảnh sản phẩm mới',
        description='Tạo một ảnh sản phẩm mới với dữ liệu đã cung cấp.',
        request=ProductImageSerializer,
        responses={201: ProductImageSerializer},
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Ảnh sản phẩm mới đã được tạo thành công!", "data": response.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary='Cập nhật một ảnh sản phẩm',
        description='Cập nhật một ảnh sản phẩm hiện có với dữ liệu đã cung cấp.',
        request=ProductImageSerializer,
        responses={200: ProductImageSerializer},
    )
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {"message": "Ảnh sản phẩm đã được cập nhật thành công!", "data": response.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary='Cập nhật một phần của ảnh sản phẩm',
        description='Cập nhật một phần của ảnh sản phẩm hiện có với dữ liệu đã cung cấp.',
        request=ProductImageSerializer,
        responses={200: ProductImageSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return Response(
            {"message": "ảnh sản phẩm đã được cập nhật thành công!", "data": response.data},
            status=status.HTTP_200_OK,
        )