from rest_framework.generics import RetrieveUpdateAPIView, DestroyAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemQuantitySerializer
from django.shortcuts import get_object_or_404
from catalogue.models import Product, ProductCombo
from rest_framework.generics import RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Cart
from .serializers import CartSerializer
from django.db import transaction
from catalogue.serializers import ProductComboSerializer

class UserCartView(RetrieveDestroyAPIView):
    """Retrieve and delete the user's cart (GET, DELETE only)."""
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        """Ensure each user can only access their own cart."""
        return Cart.objects.get(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Xóa toàn bộ sản phẩm trong giỏ hàng nhưng không xóa giỏ hàng."""
        cart = self.get_object()
        cart.cartitem_set.all().delete()  # ✅ Xóa tất cả sản phẩm trong giỏ hàng
        return Response({"message": "Đã xóa toàn bộ sản phẩm trong giỏ hàng"}, status=status.HTTP_204_NO_CONTENT)

class UpdateCartItemQuantityView(UpdateAPIView):
    """
    API để cập nhật số lượng sản phẩm trong giỏ hàng (PATCH /cart/item/{pk}/update/)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemQuantitySerializer
    http_method_names = ["patch"]  # Chỉ cho phép PATCH

    def patch(self, request, pk, *args, **kwargs):
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
            new_quantity = request.data.get("quantity")

            if new_quantity is None:
                return Response({"error": "Bạn phải gửi số lượng mới."}, status=status.HTTP_400_BAD_REQUEST)

            new_quantity = int(new_quantity)

            if new_quantity < 1:
                return Response({"error": "Số lượng phải ít nhất là 1."}, status=status.HTTP_400_BAD_REQUEST)

            cart_item.quantity = new_quantity
            cart_item.save()

            return Response(CartItemQuantitySerializer(cart_item).data, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response({"error": "Sản phẩm không tồn tại trong giỏ hàng."}, status=status.HTTP_404_NOT_FOUND)


class RemoveCartItemView(DestroyAPIView):
    """Remove an item from the cart."""
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
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

        with transaction.atomic():
            # Xử lý trường hợp có nhiều cart (nếu có)
            carts = Cart.objects.filter(user=user)
            if carts.count() > 1:
                # Giữ lại cart đầu tiên và xóa các cart còn lại
                main_cart = carts.first()
                # Di chuyển tất cả các items từ các cart khác vào main_cart
                CartItem.objects.filter(cart__in=carts.exclude(id=main_cart.id)).update(cart=main_cart)
                # Xóa các cart thừa
                carts.exclude(id=main_cart.id).delete()
                cart = main_cart
            else:
                # Nếu không có cart nào, tạo mới
                cart, _ = Cart.objects.get_or_create(user=user)

            # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

            if not item_created:
                cart_item.quantity += int(quantity)  # Cập nhật số lượng nếu đã tồn tại
            else:
                cart_item.quantity = int(quantity)

            cart_item.save()

            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

class GetApplicableCombosView(RetrieveAPIView):
    """Get all combos that can be applied to the current cart."""
    permission_classes = [IsAuthenticated]
    serializer_class = ProductComboSerializer

    def get(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()
        
        # Get all active combos
        combos = ProductCombo.objects.filter(is_active=True)
        applicable_combos = []

        for combo in combos:
            combo_items = combo.items.all()
            can_apply = True
            
            # Check if all items in the combo are in the cart with sufficient quantity
            for combo_item in combo_items:
                cart_item = cart_items.filter(product=combo_item.product).first()
                if not cart_item or cart_item.quantity < combo_item.quantity:
                    can_apply = False
                    break
            
            if can_apply:
                applicable_combos.append(combo)

        serializer = self.get_serializer(applicable_combos, many=True)
        return Response(serializer.data)
