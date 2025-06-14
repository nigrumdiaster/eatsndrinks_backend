from django.urls import path
from .views import OrderCreateView, AdminOrderView, AdminOrderDetailView, UserOrderListView, UserOrderDetailView, RecentPaidCustomersView, MonthlySalesView, MonthlyRevenueView, YearlyRevenueView

urlpatterns = [
    path("", UserOrderListView.as_view(), name="user-orders"),
    path("create", OrderCreateView.as_view(), name="user-order-create"),
    path("admin/orders/", AdminOrderView.as_view(), name="admin-order-list"),  # GET danh sách
    path("admin/order/<int:id>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),  # GET, PUT, PATCH, DELETE
    path("<int:id>/", UserOrderDetailView.as_view(), name="user-order-detail"),
    path('admin/recent-paid-customers/', RecentPaidCustomersView.as_view(), name='recent-paid-customers'),
    path('admin/monthly-sales/', MonthlySalesView.as_view(), name='monthly-sales'),
    path('admin/monthly-revenue/', MonthlyRevenueView.as_view(), name='monthly-revenue'),
    path('admin/yearly-revenue/', YearlyRevenueView.as_view(), name='yearly-revenue'),
]
