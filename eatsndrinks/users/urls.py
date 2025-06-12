from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, TokenRefreshView, AdminUserDetailView, AdminUserListView, UserDetailView, IsAdminView, AddressBookViewSet, DefaultAddressView

# Sử dụng DefaultRouter để tự động tạo URL cho AddressBookViewSet
router = DefaultRouter()
router.register(r'address-book', AddressBookViewSet, basename='address-book')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Admin: Manage all users
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),  # GET only
    path('admin/user/<int:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),  # GET, PUT, PATCH
    # User: Manage own profile
    path('user/profile/', UserDetailView.as_view(), name='user-profile'),
    path("is-admin/", IsAdminView.as_view(), name="is-admin"),

    path('address-book/default/', DefaultAddressView.as_view(), name='default-address'),
    # Include AddressBookViewSet URLs
    path('', include(router.urls)),
]
