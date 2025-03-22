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


class CategoryViewSet(
    CustomPermissionMixin, CategorySchemaMixin, viewsets.ModelViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get", "post", "put", "patch"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of products to return (optional)",
            )
        ]
    )
    @action(detail=True, methods=["get"], url_path="products")
    def get_products(self, request, pk=None):
        """Fetch products belonging to a specific category with an optional limit."""
        try:
            category = self.get_object()
            products = Product.objects.filter(category=category)

            # Get 'limit' query param, default to None (no limit)
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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPageNumberPagination
    http_method_names = ["get", "post", "put", "patch"]

    @action(detail=False, methods=["get"], url_path="random")
    def get_random_products(self, request):
        """Lấy 8 sản phẩm ngẫu nhiên"""
        random_products = Product.objects.order_by("?")[:8]
        serializer = self.get_serializer(random_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="category",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID của danh mục sản phẩm cần lọc",
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Số trang cần lấy",
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
    @action(detail=False, methods=["get"], url_path="")
    def get_products_by_category(self, request):
        """Lấy danh sách sản phẩm theo category_id và hỗ trợ pagination"""
        category_id = request.query_params.get("category")

        if not category_id:
            return Response(
                {"detail": "Thiếu tham số category."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            products = Product.objects.filter(category_id=category_id).order_by("id")

            # Áp dụng pagination
            page = self.paginate_queryset(products)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {"detail": "Giá trị category không hợp lệ."},
                status=status.HTTP_400_BAD_REQUEST,
            )
# ProductImage ViewSet
class ProductImageViewSet(
    CustomPermissionMixin, ProductImageSchemaMixin, viewsets.ModelViewSet
):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    http_method_names = ["get", "post", "put", "patch"]
