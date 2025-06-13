from rest_framework import viewsets
from rest_framework.response import Response

from .mixins import (
    CustomPermissionMixin,
    CategorySchemaMixin,
    ProductImageSchemaMixin,
    ProductSchemaMixin,
)
from .models import Category, Product, ProductImage, ProductCombo, ProductComboItem
from .serializers import (
    CategorySerializer, ProductSerializer, ProductImageSerializer,
    ProductComboSerializer, ProductComboItemSerializer
)
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
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone

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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPageNumberPagination
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    http_method_names = ["get", "post", "put", "patch"]

    def get_queryset(self):
        """Lọc sản phẩm dựa vào quyền của người dùng"""
        queryset = Product.objects.all().order_by("id")
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=["get"], url_path="random")
    def get_random_products(self, request):
        """Lấy 8 sản phẩm ngẫu nhiên"""
        queryset = self.get_queryset().order_by("?")[:8]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="flash-sale")
    def get_flash_sale_products(self, request):
        """Lấy danh sách sản phẩm đang flash sale"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            flash_sale_start__lte=now,
            flash_sale_end__gte=now,
            flash_sale_price__isnull=False,
        )

        limit = request.query_params.get("limit")
        if limit is not None:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                return Response(
                    {"detail": "Giá trị 'limit' không hợp lệ."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="set-flash-sale")
    def set_flash_sale(self, request, pk=None):
        """Gán thông tin flash sale cho sản phẩm"""
        product = self.get_object()
        flash_sale_price = request.data.get("flash_sale_price")
        flash_sale_start = request.data.get("flash_sale_start")
        flash_sale_end = request.data.get("flash_sale_end")

        if not (flash_sale_price and flash_sale_start and flash_sale_end):
            return Response(
                {"detail": "Cần truyền đầy đủ: flash_sale_price, flash_sale_start, flash_sale_end."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product.flash_sale_price = flash_sale_price
            product.flash_sale_start = flash_sale_start
            product.flash_sale_end = flash_sale_end
            product.save()
            return Response({"detail": "Cập nhật flash sale thành công."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="category", type=int, location=OpenApiParameter.QUERY, required=False, description="ID danh mục"),
            OpenApiParameter(name="search", type=str, location=OpenApiParameter.QUERY, required=False, description="Tìm kiếm theo tên"),
            OpenApiParameter(name="page", type=int, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="page_size", type=int, location=OpenApiParameter.QUERY, required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Lọc theo category, tìm kiếm theo tên, phân trang"""
        category_id = request.query_params.get("category")
        search_query = request.query_params.get("search")
        queryset = self.get_queryset()

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

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


class ProductComboViewSet(CustomPermissionMixin, viewsets.ModelViewSet):
    queryset = ProductCombo.objects.all()
    serializer_class = ProductComboSerializer
    pagination_class = ProductPageNumberPagination
    http_method_names = ["get", "post", "put", "patch"]

    def get_queryset(self):
        queryset = ProductCombo.objects.all().order_by("id")
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name="search", type=str, location=OpenApiParameter.QUERY, required=False, description="Tìm kiếm theo tên"),
            OpenApiParameter(name="page", type=int, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="page_size", type=int, location=OpenApiParameter.QUERY, required=False),
        ]
    )
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get("search")
        queryset = self.get_queryset()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        combo = self.get_object()
        serializer = ProductComboItemSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(combo=combo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"])
    def remove_item(self, request, pk=None):
        combo = self.get_object()
        item_id = request.data.get("item_id")
        
        try:
            item = combo.items.get(id=item_id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductComboItem.DoesNotExist:
            return Response(
                {"detail": "Không tìm thấy món ăn trong combo."},
                status=status.HTTP_404_NOT_FOUND
            )
