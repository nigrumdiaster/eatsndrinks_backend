from django.urls import path
from .views import UserCartView, RemoveCartItemView, AddToCartView, UpdateCartItemQuantityView

urlpatterns = [
    path("user/cart/", UserCartView.as_view(), name="user-cart"),
    path("add/", AddToCartView.as_view(), name="add-to-cart"),
    path("remove/<int:pk>/", RemoveCartItemView.as_view(), name="remove-cart-item"),
    path("update/<int:pk>/", UpdateCartItemQuantityView.as_view(), name="update-cart-item-quantity"),
]
