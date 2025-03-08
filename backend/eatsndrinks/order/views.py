from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order
from .serializers import OrderSerializer

class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class AdminOrderView(generics.ListAPIView):
    """
    Chỉ dùng để lấy danh sách đơn hàng (GET /admin/orders/)
    """
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    """
    Cho phép admin lấy, cập nhật hoặc xóa đơn hàng theo ID (GET, PUT, PATCH, DELETE)
    """
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = "id"

