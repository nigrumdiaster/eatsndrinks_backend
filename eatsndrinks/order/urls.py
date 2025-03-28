from django.urls import path
from .views import OrderCreateView, AdminOrderView, AdminOrderDetailView, UserOrderListView, UserOrderDetailView

urlpatterns = [
    path("", UserOrderListView.as_view(), name="user-orders"),
    path("create", OrderCreateView.as_view(), name="user-order-create"),
    path("admin/orders/", AdminOrderView.as_view(), name="admin-order-list"),  # GET danh sách
    path("admin/order/<int:id>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),  # GET, PUT, PATCH, DELETE
    path("<int:id>/", UserOrderDetailView.as_view(), name="user-order-detail"),
]
