from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order, OrderDetail
from .serializers import AdminOrderSerializer, OrderSerializer, OrderDetailSerializer
from rest_framework.response import Response
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

class AdminOrderView(generics.ListAPIView):
    """
    API để admin lấy danh sách đơn hàng (GET /admin/orders/)
    """
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all().order_by("-created_at")  # Sắp xếp theo thời gian tạo
    serializer_class = AdminOrderSerializer

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


