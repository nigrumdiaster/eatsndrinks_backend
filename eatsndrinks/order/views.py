from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order, OrderDetail
from .serializers import AdminOrderSerializer, OrderSerializer, OrderDetailSerializer, RecentCustomerSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.utils.timezone import now
from django.db.models import Sum

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

class RecentPaidCustomersView(APIView):
    """
    API để lấy thông tin 5 khách hàng gần đây đã thanh toán
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Lấy danh sách 5 đơn hàng đã thanh toán gần đây
        recent_orders = Order.objects.filter(payment_status="paid").order_by("-created_at")[:5]
        
        # Serialize dữ liệu
        serializer = RecentCustomerSerializer(recent_orders, many=True)
        return Response(serializer.data, status=200)

class MonthlySalesView(APIView):
    """
    API để trả về số lượng đơn hàng đã thanh toán trong tháng này
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        today = now()
        start_of_month = today.replace(day=1)
        # Tính ngày đầu tháng tiếp theo
        if today.month < 12:
            end_of_month = today.replace(month=today.month + 1, day=1)
        else:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1)

        # Lọc các đơn hàng đã thanh toán trong tháng này
        orders = Order.objects.filter(
            payment_status="paid",
            created_at__gte=start_of_month,
            created_at__lt=end_of_month
        )

        total_orders = orders.count()

        return Response({"total_quantity": total_orders}, status=200)

class MonthlyRevenueView(APIView):
    """
    API để trả về tổng doanh thu tháng này và phần trăm tăng/giảm so với tháng trước
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Lấy ngày đầu tiên và ngày cuối cùng của tháng hiện tại
        today = now()
        start_of_this_month = today.replace(day=1)
        if today.month < 12:
            start_of_next_month = today.replace(day=1, month=today.month + 1)
        else:
            start_of_next_month = today.replace(day=1, month=1, year=today.year + 1)

        # Lấy ngày đầu tiên và ngày cuối cùng của tháng trước
        if today.month > 1:
            start_of_last_month = today.replace(day=1, month=today.month - 1)
        else:
            start_of_last_month = today.replace(day=1, month=12, year=today.year - 1)

        # Tổng doanh thu tháng này
        revenue_this_month = Order.objects.filter(
            payment_status="paid",
            created_at__gte=start_of_this_month,
            created_at__lt=start_of_next_month
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # Tổng doanh thu tháng trước
        revenue_last_month = Order.objects.filter(
            payment_status="paid",
            created_at__gte=start_of_last_month,
            created_at__lt=start_of_this_month
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # Tính phần trăm tăng/giảm
        if revenue_last_month > 0:
            percentage_change = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
        else:
            percentage_change = None  # Không thể tính phần trăm nếu tháng trước không có doanh thu

        return Response({
            "revenue_this_month": revenue_this_month,
            "revenue_last_month": revenue_last_month,
            "percentage_change": percentage_change
        }, status=200)


