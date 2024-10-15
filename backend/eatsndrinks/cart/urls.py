from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

router = DefaultRouter()
router.register(r'carts', CartViewSet)

urlpatterns = [
    # Other URL patterns
    path('', include(router.urls)),
]
