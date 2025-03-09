from django.urls import path
from .views import OrderCreateView, AdminOrderView, AdminOrderDetailView

urlpatterns = [
    path("", OrderCreateView.as_view(), name="user-order"),
    path("admin/orders/", AdminOrderView.as_view(), name="admin-order-list"),  # GET danh sách
    path("admin/order/<int:id>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),  # GET, PUT, PATCH, DELETE
]
