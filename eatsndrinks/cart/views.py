from rest_framework.generics import RetrieveUpdateAPIView, DestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404
from catalogue.models import Product

class UserCartView(RetrieveUpdateAPIView):
    """Retrieve and update the user's cart."""
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        """Ensure each user can only access their own cart."""
        return Cart.objects.get(user=self.request.user)

class RemoveCartItemView(DestroyAPIView):
    """Remove an item from the cart."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
            cart_item.delete()
            return Response({"message": "Item removed from cart."}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

class AddToCartView(CreateAPIView):
    """Add a product to the cart."""
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        product = get_object_or_404(Product, pk=product_id)

        # Kiểm tra xem giỏ hàng đã tồn tại chưa, nếu chưa thì tạo mới
        cart, created = Cart.objects.get_or_create(user=user)

        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            cart_item.quantity += int(quantity)  # Cập nhật số lượng nếu đã tồn tại
        else:
            cart_item.quantity = int(quantity)

        cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
