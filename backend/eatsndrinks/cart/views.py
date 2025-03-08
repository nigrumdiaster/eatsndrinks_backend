from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Cart
from .serializers import CartSerializer

class UserCartView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        """Ensure each user can only access their own cart."""
        return Cart.objects.get(user=self.request.user)
