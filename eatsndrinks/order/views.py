from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order, OrderDetail
from .serializers import AdminOrderSerializer, OrderSerializer, OrderDetailSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class UserOrderListView(generics.ListAPIView):
    """
    API trả về danh sách đơn hàng của người dùng hiện tại (GET /orders/)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")  # Lấy đơn hàng của user, mới nhất trước

class UserOrderDetailView(generics.RetrieveAPIView):
    """
    API lấy thông tin chi tiết đơn hàng của user theo order_id (GET /orders/{order_id}/)
    """
    permission_classes = [IsAuthenticated]  # Chỉ user đăng nhập mới truy cập
    serializer_class = OrderSerializer
    lookup_field = "id"

    def get_queryset(self):
        # Chỉ lấy đơn hàng thuộc về user hiện tại
        return Order.objects.filter(user=self.request.user)

class OrderPageNumberPagination(PageNumberPagination):
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

class AdminOrderView(generics.ListAPIView):
    """
    API để admin lấy danh sách đơn hàng (GET /admin/orders/)
    """
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all().order_by("-created_at")  # Sắp xếp theo thời gian tạo
    serializer_class = AdminOrderSerializer
    pagination_class = OrderPageNumberPagination

    def filter_queryset(self, queryset):
        """
        Thêm chức năng tìm kiếm và lọc theo trạng thái, phương thức thanh toán, trạng thái thanh toán
        """
        # Lọc theo mã đơn hàng hoặc tên người dùng
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(
                id__icontains=search_query
            )

        # Lọc theo trạng thái đơn hàng
        status = self.request.query_params.get("status", None)
        if status:
            queryset = queryset.filter(status=status)

        # Lọc theo phương thức thanh toán
        payment_method = self.request.query_params.get("payment_method", None)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        # Lọc theo trạng thái thanh toán
        payment_status = self.request.query_params.get("payment_status", None)
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        return queryset

    def get_queryset(self):
        """
        Gọi filter_queryset để áp dụng tìm kiếm và lọc
        """
        queryset = super().get_queryset()
        return self.filter_queryset(queryset)

class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    """
    API để admin xem & cập nhật đơn hàng theo ID (GET, PUT, PATCH)
    - Không cho phép DELETE (xóa)
    """
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = AdminOrderSerializer
    lookup_field = "id"
    http_method_names = ["get", "post", "put", "patch"]


