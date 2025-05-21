from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicRestaurantViewSet, AdminRestaurantViewSet

public_router = DefaultRouter()
public_router.register(r'restaurants', PublicRestaurantViewSet, basename='public-restaurant')

admin_router = DefaultRouter()
admin_router.register(r'restaurants', AdminRestaurantViewSet, basename='admin-restaurant')

urlpatterns = [
    path('public/', include(public_router.urls)),  # /api/public/restaurants/
    path('admin/', include(admin_router.urls)),    # /api/admin/restaurants/
]
