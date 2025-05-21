from rest_framework import viewsets, permissions
from .models import Restaurant
from .serializers import RestaurantSerializer

# API cho người dùng (chỉ đọc, chỉ thấy is_active=True)
class PublicRestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Restaurant.objects.filter(is_active=True)
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]  # hoặc tùy chỉnh theo nhu cầu

# API cho admin (đầy đủ quyền)
class AdminRestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAdminUser]
