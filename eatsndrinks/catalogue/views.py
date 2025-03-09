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


# ProductImage ViewSet
class ProductImageViewSet(
    CustomPermissionMixin, ProductImageSchemaMixin, viewsets.ModelViewSet
):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    http_method_names = ["get", "post", "put", "patch"]
