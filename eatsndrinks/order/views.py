from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order
from .serializers import AdminOrderSerializer, OrderSerializer
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


