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


# Category ViewSet
class CategoryViewSet(
    CustomPermissionMixin, CategorySchemaMixin, viewsets.ModelViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get", "post", "put", "patch"]


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


# ProductImage ViewSet
class ProductImageViewSet(
    CustomPermissionMixin, ProductImageSchemaMixin, viewsets.ModelViewSet
):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    http_method_names = ["get", "post", "put", "patch"]
