# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.exceptions import PermissionDenied

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter carts to only show the authenticated user's cart
        return Cart.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        cart = self.get_object()
        if cart.user != request.user:
            raise PermissionDenied("Bạn không có quyền truy cập giỏ hàng này.")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        cart = self.get_object()
        if cart.user != request.user:
            raise PermissionDenied("Bạn không có quyền sửa giỏ hàng này.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        cart = self.get_object()
        if cart.user != request.user:
            raise PermissionDenied("Bạn không có quyền xóa giỏ hàng này.")
        return super().destroy(request, *args, **kwargs)
