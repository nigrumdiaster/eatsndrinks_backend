from django.urls import path
from .views import UserCartView, RemoveCartItemView, AddToCartView

urlpatterns = [
    path("user/cart/", UserCartView.as_view(), name="user-cart"),
    path("add/", AddToCartView.as_view(), name="add-to-cart"),
    path("remove/<int:pk>/", RemoveCartItemView.as_view(), name="remove-cart-item"),
]
