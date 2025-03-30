from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, reply_to_contact

router = DefaultRouter()
router.register(r'', ContactViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('/reply/', reply_to_contact, name='reply_to_contact'),
]
