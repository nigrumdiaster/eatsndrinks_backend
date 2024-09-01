from rest_framework import viewsets
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
# Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get", "post", "put", "patch"]

    def get_permissions(self):
        """
        Đặt quyền truy cập cho từng phương thức.
        """
        if self.request.method == 'GET':
            permission_classes = [AllowAny]  # Phân quyền cho phương thức GET
        elif self.request.method in ['POST', 'PUT', 'PATCH']:
            permission_classes = [IsAdminUser]  # Phân quyền cho phương thức POST, PUT, PATCH

        return [permission() for permission in permission_classes]


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


# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ["get", "post", "put", "patch"]

    def get_permissions(self):
        """
        Đặt quyền truy cập cho từng phương thức.
        """
        if self.request.method == 'GET':
            permission_classes = [AllowAny]  # Phân quyền cho phương thức GET
        elif self.request.method in ['POST', 'PUT', 'PATCH']:
            permission_classes = [IsAdminUser]  # Phân quyền cho phương thức POST, PUT, PATCH
            
        return [permission() for permission in permission_classes]

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