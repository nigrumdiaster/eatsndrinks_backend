from django.urls import path
from .views import RegisterView, LoginView, TokenRefreshView, AdminUserDetailView,AdminUserListView, UserDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Admin: Manage all users
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),  # GET only
    path('admin/user/<int:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),  # GET, PUT, PATCH
    # User: Manage own profile
    path('user/profile/', UserDetailView.as_view(), name='user-profile'),
]
