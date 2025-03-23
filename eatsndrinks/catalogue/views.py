from rest_framework import viewsets
from rest_framework.response import Response

from .mixins import (
    CustomPermissionMixin,
    CategorySchemaMixin,
    ProductImageSchemaMixin,
    ProductSchemaMixin,
)
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.paginator import Paginator, EmptyPage
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser


class CategoryViewSet(
    CustomPermissionMixin, CategorySchemaMixin, viewsets.ModelViewSet
):
    queryset = Category.objects.all()  # ✅ Thêm queryset
    serializer_class = CategorySerializer
    http_method_names = ["get", "post", "put", "patch"]

    def get_queryset(self):
        """Chỉ hiển thị danh mục is_active=True nếu người dùng không phải admin"""
        queryset = Category.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=True, methods=["get"], url_path="products")
    def get_products(self, request, pk=None):
        """Chỉ trả về sản phẩm is_active=True thuộc category nếu là user thường"""
        try:
            category = self.get_object()
            products = Product.objects.filter(category=category)

            if not request.user.is_staff:
                products = products.filter(is_active=True)  # ✅ Lọc sản phẩm active

            limit = request.query_params.get("limit")
            if limit is not None:
                try:
                    limit = int(limit)
                    products = products[:limit]
                except ValueError:
                    return Response(
                        {"detail": "Invalid limit value. Must be an integer."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer = ProductSerializer(
                products, many=True, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response(
                {"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ProductPageNumberPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = (
        "page_size"  # Allow clients to set page size using this query parameter
    )
    max_page_size = 100  # Maximum number of items that can be requested per page

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,  # Add total pages here
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


# Product ViewSet
class ProductViewSet(CustomPermissionMixin, ProductSchemaMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()  # ✅ Thêm queryset ở đây
    serializer_class = ProductSerializer
    pagination_class = ProductPageNumberPagination
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ["get", "post", "put", "patch"]

    def get_queryset(self):
        """Lọc sản phẩm dựa vào quyền của người dùng"""
        queryset = Product.objects.all().order_by("id")
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=["get"], url_path="random")
    def get_random_products(self, request):
        """Lấy 8 sản phẩm ngẫu nhiên (chỉ lấy sản phẩm đang hoạt động nếu không phải admin)"""
        queryset = self.get_queryset().order_by("?")[:8]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="category",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="ID của danh mục sản phẩm cần lọc",
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Tìm kiếm sản phẩm theo tên",
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Chỉ số trang cần lấy",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Số lượng sản phẩm mỗi trang (mặc định: 10, tối đa: 100)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Lấy danh sách sản phẩm (lọc theo category, tìm kiếm theo tên, hỗ trợ pagination)"""
        category_id = request.query_params.get("category")
        search_query = request.query_params.get("search")

        queryset = self.get_queryset()  # Lọc dữ liệu dựa trên quyền truy cập

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            )  # Tìm kiếm không phân biệt hoa thường

        # Áp dụng pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ProductImage ViewSet
class ProductImageViewSet(
    CustomPermissionMixin, ProductImageSchemaMixin, viewsets.ModelViewSet
):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    http_method_names = ["get", "post", "put", "patch"]
